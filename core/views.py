from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Sum
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Category, MenuItem, Order, Table


def home(request: HttpRequest) -> HttpResponse:
    featured_items = (
        MenuItem.objects.filter(is_available=True)
        .select_related("category")
        .order_by("-id")[:3]
    )
    stats = {
        "category_count": Category.objects.count(),
        "menu_item_count": MenuItem.objects.filter(is_available=True).count(),
        "active_tables": Table.objects.exclude(status=Table.STATUS_AVAILABLE).count(),
        "open_orders": Order.objects.exclude(status=Order.STATUS_CLOSED).count(),
    }
    context = {
        "featured_items": featured_items,
        "stats": stats,
    }
    return render(request, "core/home.html", context)


def menu_page(request: HttpRequest) -> HttpResponse:
    items = (
        MenuItem.objects.filter(is_available=True)
        .exclude(name__icontains="chicken")
        .exclude(name__icontains="mutton")
        .exclude(name__icontains="egg")
        .select_related("category")
        .order_by("category__name", "name")
    )
    return render(request, "core/menu.html", {"items": items})


def order_page(request: HttpRequest) -> HttpResponse:
    table_id = request.GET.get("table")
    if not table_id:
        raise Http404("Table not specified")
    table = get_object_or_404(Table, id=table_id)
    items = (
        MenuItem.objects.filter(is_available=True)
        .exclude(name__icontains="chicken")
        .exclude(name__icontains="mutton")
        .exclude(name__icontains="egg")
        .order_by("name")
    )
    return render(
        request,
        "core/order.html",
        {
            "table": table,
            "items": items,
        },
    )


def order_status_page(request: HttpRequest, order_id: int) -> HttpResponse:
    order = get_object_or_404(Order, id=order_id)
    return render(request, "core/order_status.html", {"order": order})


def _staff_check(user):
    return bool(user and user.is_staff)


def staff_required(view_func):
    decorated = login_required(user_passes_test(_staff_check)(view_func))
    return decorated


@staff_required
def admin_dashboard(request: HttpRequest) -> HttpResponse:
    total_revenue = (
        Order.objects.filter(status__in=[Order.STATUS_SERVED, Order.STATUS_CLOSED])
        .aggregate(total=Sum("total_price"))
        .get("total")
        or 0
    )
    # Daily revenue (SQLite dev-friendly); swap to proper date filter for PostgreSQL
    daily_revenue = (
        Order.objects.filter(status__in=[Order.STATUS_SERVED, Order.STATUS_CLOSED])
        .extra(where=["date(created_at) = date('now')"])
        .aggregate(total=Sum("total_price"))
        .get("total")
        or 0
    )
    active_orders = (
        Order.objects.exclude(status=Order.STATUS_CLOSED)
        .select_related("table")
        .order_by("-created_at")[:20]
    )
    table_stats = (
        Table.objects.values("status")
        .annotate(count=Count("id"))
        .order_by("status")
    )
    popular_dishes = (
        MenuItem.objects.filter(
            order_items__order__status__in=[
                Order.STATUS_SERVED,
                Order.STATUS_CLOSED,
            ]
        )
        .annotate(times_ordered=Count("order_items"))
        .order_by("-times_ordered")[:5]
    )
    context = {
        "total_revenue": total_revenue,
        "daily_revenue": daily_revenue,
        "active_orders": active_orders,
        "table_stats": table_stats,
        "popular_dishes": popular_dishes,
    }
    return render(request, "core/admin_dashboard.html", context)


def staff_login(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("admin_dashboard")
    message = ""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect("admin_dashboard")
        message = "Invalid credentials or not authorized as staff."
    return render(request, "core/staff_login.html", {"message": message})


def staff_logout(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        logout(request)
    return redirect("home")