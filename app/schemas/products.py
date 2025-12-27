from dataclasses import dataclass
from datetime import datetime

import polars
import pydantic
from pydantic import Field, computed_field


class Product(pydantic.BaseModel):
    # Core identification
    product_id: str = Field(alias="Numero")
    name: str = Field(alias="Nimi")
    manufacturer: str | None = Field(alias="Valmistaja")

    # Pricing and sizing
    bottle_size: str | None = Field(alias="Pullokoko")
    price: float | None = Field(alias="Hinta")
    price_per_liter: float | None = Field(alias="Litrahinta")

    # Categorization
    is_novelty: bool = Field(alias="Uutuus", default=False)
    category: str | None = Field(alias="Tyyppi")
    sub_category: str | None = Field(alias="Alatyyppi", default=None)
    beer_type: str | None = Field(alias="Oluttyyppi", default=None)
    special_group: str | None = Field(alias="Erityisryhmä", default=None)

    # Origin and vintage
    country: str | None = Field(alias="Valmistusmaa")
    region: str | None = Field(alias="Alue", default=None)
    year: int | None = Field(alias="Vuosikerta", default=None)

    # Technical specs
    alcohol_percent: float | None = Field(alias="Alkoholi-%")
    acids_g_l: float | None = Field(alias="Hapot g/l", default=None)
    sugar_g_l: float | None = Field(alias="Sokeri g/l", default=None)
    energy_kcal: float | None = Field(alias="Energia kcal/100 ml", default=None)

    # Packaging
    package_type: str | None = Field(alias="Pakkaustyyppi")
    closure_type: str | None = Field(alias="Suljentatyyppi", default=None)
    ean: str | None = Field(alias="EAN", default=None)

    # Description and flavor
    description: str = Field(alias="Luonnehdinta", default="")
    grapes: str | None = Field(alias="Rypäleet", default=None)
    notes: str | None = Field(alias="Huomautus", default=None)

    @computed_field
    @property
    def image_link(self) -> str:
        return f"https://images.alko.fi/images/cs_srgb,f_auto,t_medium/cdn/{self.product_id}/.jpg"

    @computed_field
    @property
    def link(self) -> str:
        return f"https://www.alko.fi/tuotteet/{self.product_id}/"

    model_config = pydantic.ConfigDict(populate_by_name=True)


@dataclass
class ProductDatabase:
    df: polars.DataFrame
    updated_at: datetime
    product_count: int
