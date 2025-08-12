import logging
import time
import random
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from datadog import initialize, api
import requests

# Import ddtrace for APM tracing
try:
    from ddtrace import tracer
    DDTRACE_AVAILABLE = True
except ImportError:
    DDTRACE_AVAILABLE = False

# Initialize Datadog
if settings.DD_API_KEY:
    initialize(api_key=settings.DD_API_KEY, app_key=settings.DD_APP_KEY)

logger = logging.getLogger(__name__)

def home(request):
    """Home page with basic Datadog metrics"""
    logger.info("Home page accessed")
    
    # Send custom metric to Datadog
    if settings.DD_API_KEY:
        try:
            api.Metric.send(
                metric='django.page.views',
                points=[(time.time(), 1)],
                tags=['page:home', 'environment:development']
            )
        except Exception as e:
            logger.error(f"Failed to send Datadog metric: {e}")
    
    context = {
        'title': 'Django + Datadog Demo',
        'datadog_enabled': bool(settings.DD_API_KEY),
        'rum_enabled': True,  # RUM is now hardcoded in base.html
    }
    return render(request, 'main/home.html', context)

def metrics(request):
    """Display application metrics"""
    logger.info("Metrics page accessed")
    
    # Simulate some metrics
    metrics_data = {
        'cpu_usage': random.randint(20, 80),
        'memory_usage': random.randint(30, 90),
        'request_count': random.randint(100, 1000),
        'error_rate': round(random.uniform(0.1, 5.0), 2),
        'response_time': random.randint(50, 500),
    }
    
    # Send metrics to Datadog
    if settings.DD_API_KEY:
        try:
            current_time = time.time()
            for metric_name, value in metrics_data.items():
                api.Metric.send(
                    metric=f'django.app.{metric_name}',
                    points=[(current_time, value)],
                    tags=['environment:development', 'app:django-demo']
                )
            logger.info("Metrics sent to Datadog successfully")
        except Exception as e:
            logger.error(f"Failed to send metrics to Datadog: {e}")
    
    context = {
        'title': 'Application Metrics',
        'metrics': metrics_data,
        'datadog_enabled': bool(settings.DD_API_KEY),
    }
    return render(request, 'main/metrics.html', context)

def api_test(request):
    """Test API endpoint with logging and metrics"""
    logger.info("API test endpoint called")
    
    # Create custom span for detailed APM tracing
    if DDTRACE_AVAILABLE and settings.DD_API_KEY:
        with tracer.trace("api.test.processing", service="django-datadog-app") as span:
            span.set_tag("endpoint", "api_test")
            span.set_tag("user_agent", request.META.get('HTTP_USER_AGENT', 'unknown'))
            
            # Simulate some processing time
            processing_time = random.uniform(0.1, 2.0)
            span.set_tag("processing_time", processing_time)
            
            # Simulate database operation with custom span
            with tracer.trace("db.query.simulation", service="django-db") as db_span:
                db_span.set_tag("query_type", "SELECT")
                db_span.set_tag("table", "test_table")
                time.sleep(processing_time * 0.3)  # 30% of time for "DB query"
            
            # Simulate external API call with custom span
            with tracer.trace("http.client.external_api", service="external-api") as http_span:
                http_span.set_tag("http.method", "GET")
                http_span.set_tag("http.url", "https://api.example.com/data")
                time.sleep(processing_time * 0.2)  # 20% of time for "external API"
            
            # Rest of processing
            time.sleep(processing_time * 0.5)  # 50% of time for business logic
    else:
        # Simulate some processing time
        processing_time = random.uniform(0.1, 2.0)
        time.sleep(processing_time)
    
    # Generate some test data
    test_data = {
        'status': 'success',
        'message': 'API is working correctly',
        'processing_time_ms': round(processing_time * 1000, 2),
        'timestamp': time.time(),
        'random_value': random.randint(1, 100),
    }
    
    # Log success or simulate random errors
    if random.random() < 0.1:  # 10% chance of error
        logger.error("Simulated API error occurred")
        test_data['status'] = 'error'
        test_data['message'] = 'Simulated error for testing'
        
        # Send error metric to Datadog
        if settings.DD_API_KEY:
            try:
                api.Metric.send(
                    metric='django.api.errors',
                    points=[(time.time(), 1)],
                    tags=['endpoint:api_test', 'environment:development']
                )
            except Exception as e:
                logger.error(f"Failed to send error metric to Datadog: {e}")
        
        return JsonResponse(test_data, status=500)
    else:
        logger.info(f"API test completed successfully in {processing_time:.2f}s")
        
        # Send success metrics to Datadog
        if settings.DD_API_KEY:
            try:
                current_time = time.time()
                api.Metric.send(
                    metric='django.api.requests',
                    points=[(current_time, 1)],
                    tags=['endpoint:api_test', 'status:success', 'environment:development']
                )
                api.Metric.send(
                    metric='django.api.response_time',
                    points=[(current_time, processing_time * 1000)],
                    tags=['endpoint:api_test', 'environment:development']
                )
            except Exception as e:
                logger.error(f"Failed to send success metrics to Datadog: {e}")
    
    return JsonResponse(test_data)

def health_check(request):
    """Health check endpoint for monitoring"""
    logger.debug("Health check requested")
    
    health_data = {
        'status': 'healthy',
        'timestamp': time.time(),
        'datadog_configured': bool(settings.DD_API_KEY),
        'database': 'connected',  # In a real app, you'd check DB connection
        'version': '1.0.0',
    }
    
    return JsonResponse(health_data)
