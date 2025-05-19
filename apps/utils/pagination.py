from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

def paginate_queryset(request, queryset, per_page=10):
    """
    Fungsi utilitas untuk melakukan paginasi pada queryset
    
    Args:
        request: HttpRequest object
        queryset: Django QuerySet yang akan dipaginasi
        per_page: Jumlah item per halaman (default: 10)
        
    Returns:
        Objek page yang berisi hasil paginasi
    """
    paginator = Paginator(queryset, per_page)
    page = request.GET.get('page')
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        # Jika page bukan integer, tampilkan halaman pertama
        page_obj = paginator.page(1)
    except EmptyPage:
        # Jika page diluar range, tampilkan halaman terakhir
        page_obj = paginator.page(paginator.num_pages)
        
    return page_obj