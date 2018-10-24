import math


def paginate(page, total_items, total_pages, slice_size=5):
    """
    Paginate
    Does some maths to generate ranged pagination. Returns a dictionary
    of page numbers to be used in url builders that allows to go to first
    page, previous page, next page, last page and one of the pages in
    range around current page with possibility to jump in slices. The
    result will look like this:

        {
            page: 2,
            total_pages: 100,
            total_items: 1000,
            pagination: {
                first: 1
                previous: 1,
                previous_slice: 1
                pages: [1, 2, 3, 4, 5, 6, 7 ... etc]
                next_slice: 14
                next: 3,
                last: 100
            }

        }
    :return: boiler.collections.paginated_collection.PaginatedCollection
    """
    if slice_size > total_pages:
        slice_size = total_pages

    # paginate (can be out of bounds for now)
    first = 1
    previous = page - 1
    next = page + 1
    last = total_pages
    previous_slice = page - slice_size
    next_slice = page + slice_size

    # assemble
    links = dict(
        first=None,
        previous=None,
        next=None,
        last=None
    )

    # previous/next
    if total_pages > 1:
        if page == 1:
            links['next'] = next
            links['last'] = last
        elif page == total_pages:
            links['first'] = first
            links['previous'] = previous
        else:
            links['first'] = first
            links['previous'] = previous
            links['next'] = next
            links['last'] = last

    # previous_slice
    links['previous_slice'] = previous_slice
    if page - slice_size <= 0:
        links['previous_slice'] = None
        if page != 1:
            links['previous_slice'] = first

    # next slice
    links['next_slice'] = next_slice
    if page + slice_size > total_pages:
        links['next_slice'] = None
        if page != total_pages and total_pages != 0:
            links['next_slice'] = last

    # slice pages
    delta = math.ceil(slice_size / 2)
    if page - delta > total_pages - slice_size:
        left_bound = total_pages - slice_size + 1
        right_bound = total_pages
    else:
        if page - delta < 0:
            delta = page

        offset = page - delta
        left_bound = offset + 1
        right_bound = offset + slice_size

    # append page range
    links['pages'] = list(range(left_bound, right_bound + 1))

    # discard slice navigation if no next/prev slice
    if links['pages']:
        if links['previous_slice'] == links['pages'][0]:
            links['previous_slice'] = None
        if links['next_slice'] == links['pages'][-1]:
            links['next_slice'] = None

    # and return
    pagination = dict(
        page=page,
        total_pages=total_pages,
        total_items=total_items,
        pagination=links
    )

    return pagination