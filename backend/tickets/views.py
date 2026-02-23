from django.db.models import Q, Count, Avg
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import timedelta

from .models import Ticket
from .serializers import (
    TicketSerializer,
    ClassificationRequestSerializer,
    ClassificationResponseSerializer
)
from .services import TicketClassifier


class TicketViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Ticket CRUD operations
    """
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    
    def get_queryset(self):
        """
        Filter queryset based on query parameters
        Supports: category, priority, status, search
        """
        queryset = Ticket.objects.all()
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by priority
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Filter by status
        ticket_status = self.request.query_params.get('status')
        if ticket_status:
            queryset = queryset.filter(status=ticket_status)
        
        # Search in title and description
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """
        Create a new ticket
        Returns 201 on success
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    
    def partial_update(self, request, *args, **kwargs):
        """
        Partially update a ticket (PATCH)
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'], url_path='stats')
    def get_stats(self, request):
        """
        GET /api/tickets/stats/
        Returns aggregated statistics using Django ORM
        """
        # Get all tickets
        all_tickets = Ticket.objects.all()
        
        # Total tickets
        total_tickets = all_tickets.count()
        
        # Open tickets
        open_tickets = all_tickets.filter(status='open').count()
        
        # Calculate average tickets per day
        if total_tickets > 0:
            oldest_ticket = all_tickets.order_by('created_at').first()
            if oldest_ticket:
                days_since_first = (timezone.now() - oldest_ticket.created_at).days
                # Ensure at least 1 day to avoid division by zero
                days_since_first = max(days_since_first, 1)
                avg_tickets_per_day = round(total_tickets / days_since_first, 2)
            else:
                avg_tickets_per_day = 0.0
        else:
            avg_tickets_per_day = 0.0
        
        # Priority breakdown using ORM aggregation
        priority_breakdown = dict(
            all_tickets.values('priority')
            .annotate(count=Count('id'))
            .values_list('priority', 'count')
        )
        
        # Category breakdown using ORM aggregation
        category_breakdown = dict(
            all_tickets.values('category')
            .annotate(count=Count('id'))
            .values_list('category', 'count')
        )
        
        return Response({
            'total_tickets': total_tickets,
            'open_tickets': open_tickets,
            'avg_tickets_per_day': avg_tickets_per_day,
            'priority_breakdown': priority_breakdown,
            'category_breakdown': category_breakdown,
        })
    
    @action(detail=False, methods=['post'], url_path='classify')
    def classify_ticket(self, request):
        """
        POST /api/tickets/classify/
        Classify ticket description using Gemini API
        """
        # Validate request
        request_serializer = ClassificationRequestSerializer(data=request.data)
        if not request_serializer.is_valid():
            return Response(
                request_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        description = request_serializer.validated_data['description']
        
        # Classify using Gemini
        classifier = TicketClassifier()
        result = classifier.classify(description)
        
        if result:
            # Validate response
            response_serializer = ClassificationResponseSerializer(data=result)
            if response_serializer.is_valid():
                return Response(response_serializer.data)
            else:
                # Return fallback if validation fails
                return Response({
                    'suggested_category': 'general',
                    'suggested_priority': 'medium',
                    'classification_mode': 'heuristic'
                })
        else:
            # Return fallback if classification fails
            return Response({
                'suggested_category': 'general',
                'suggested_priority': 'medium',
                'classification_mode': 'heuristic'
            })
