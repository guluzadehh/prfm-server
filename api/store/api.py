from enum import Enum
from typing import List
from django.http import Http404, HttpRequest
from ninja import Query, Router

from account.helpers import adjango_auth

from .models import Brand, Favorite, Group, Order, OrderItem, Product
from .schemas import *
from .filters import ProductFilter

router = Router()


@router.get("/brands/", response=List[BrandOutSchema])
async def brand_list(request: HttpRequest):
    brands = [brand async for brand in Brand.objects.all()]
    return brands


@router.get("/groups/", response=List[GroupOutSchema])
async def group_list(request: HttpRequest):
    groups = [group async for group in Group.objects.all()]
    return groups


class OrderChoices(Enum):
    NAME_ASC = "name"
    NAME_DESC = "-name"
    PRICE_PER_GRAM_ASC = "price_per_gram"
    PRICE_PER_GRAM_DESC = "-price_per_gram"
    SALES = "-sales"


PAGE_SIZE = 8


@router.get("/products/", response={200: ProductListOutSchema, 422: None})
async def product_list(
    request: HttpRequest,
    filters: ProductFilter = Query(...),
    ordering: OrderChoices = None,
    page: Optional[int] = None,
):
    if page is None:
        page = 1

    if page < 1:
        return 422, {"data": [], "count": 0, "next": 1, "previous": 0}

    user = await request.auser()
    products = Product.objects.all().distinct().with_favorite(user)  # type: ignore

    products = filters.filter(products)

    if ordering is not None:
        products = products.order_by(ordering.value)

    offset = (page - 1) * PAGE_SIZE
    count = await products.acount()
    products = products[offset : offset + PAGE_SIZE]
    products = [product async for product in products]

    return {
        "data": products,
        "count": count,
        "next": page + 1 if page * PAGE_SIZE < count else None,
        "previous": page - 1 if page - 1 > 0 else None,
    }


@router.get("/products/{brand_slug}_{product_slug}", response=DetailedProductOutSchema)
async def product_detail(request: HttpRequest, brand_slug: str, product_slug: str):
    user = await request.auser()

    product = (
        await (
            Product.objects.filter(brand__slug=brand_slug, slug=product_slug)
            # .prefetch_related("groups")
            .with_favorite(user).afirst()  # type: ignore
        )
    )

    if product is None:
        raise Http404

    return product


@router.get(
    "/products/{brand_slug}_{product_slug}/groups", response=List[GroupOutSchema]
)
async def group_list_of_product(
    request: HttpRequest, brand_slug: str, product_slug: str
):
    product = await Product.objects.filter(
        brand__slug=brand_slug, slug=product_slug
    ).afirst()

    if product is None:
        raise Http404

    return [group async for group in product.groups.all()]


@router.get("/favorites/", auth=adjango_auth, response=List[FavoriteOutSchema])
async def favorite_list(request: HttpRequest):
    user = await request.auser()
    favorites = (
        Favorite.objects.select_related("product", "product__brand")
        .filter(user=user)
        .all()
    )

    output = []

    async for favorite in favorites:
        favorite.product.favorite_id = favorite.id
        output.append(favorite)

    return output


@router.post(
    "/favorites/",
    auth=adjango_auth,
    response={201: FavoriteOutSchema, 422: None, 409: None},
)
async def favorite_create(request: HttpRequest, details: FavoriteInSchema):
    product = await Product.objects.filter(id=details.product_id).afirst()

    if product is None:
        return 422, None

    user = await request.auser()

    if await user.favorites.filter(product=product).aexists():
        return 409, None

    favorite = await user.favorites.acreate(product=product)

    return 201, favorite


@router.delete(
    "/favorites/{favorite_id}/", auth=adjango_auth, response={204: None, 404: None}
)
async def favorite_destroy(request: HttpRequest, favorite_id: int):
    user = await request.auser()
    favorite = await Favorite.objects.filter(id=favorite_id, user=user).afirst()

    if favorite is None:
        return 404, None

    await favorite.adelete()

    return 204, None


@router.get("/orders/", auth=adjango_auth, response=List[OrderOutSchema])
async def order_list(request: HttpRequest):
    user = await request.auser()
    orders = Order.objects.filter(user=user).prefetch_def(user).order_by("-ordered_at")

    return [order async for order in orders]


@router.post("/orders/", auth=adjango_auth, response={201: OrderOutSchema, 422: None})
async def order_create(request: HttpRequest, order_details: OrderInSchema):
    user = await request.auser()

    product_ids = list(map(lambda item: item.product_id, order_details.items))

    if await Product.objects.filter(id__in=product_ids).acount() != len(product_ids):
        return 422, None

    order = await Order.objects.acreate(
        user=user,
        email=user.email,
        phone=order_details.phone,
        address=order_details.address,
        commentary=order_details.commentary,
    )

    items = []
    for item in order_details.items:
        items.append(
            OrderItem(
                order=order,
                product_id=item.product_id,
                size=item.size,
                quantity=item.quantity,
            )
        )

    await OrderItem.objects.abulk_create(items)
    # email

    return 201, await Order.objects.prefetch_def(user).aget(id=order.id)
