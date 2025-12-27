import pydantic
from pydantic import Field, computed_field
from typing import Optional

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
    sub_category: Optional[str] = Field(alias="Alatyyppi", default=None)
    beer_type: Optional[str] = Field(alias="Oluttyyppi", default=None)
    special_group: Optional[str] = Field(alias="Erityisryhmä", default=None)
    
    # Origin and vintage
    country: str | None = Field(alias="Valmistusmaa")
    region: Optional[str] = Field(alias="Alue", default=None)
    year: Optional[int] = Field(alias="Vuosikerta", default=None)
    
    # Technical specs
    alcohol_percent: float | None = Field(alias="Alkoholi-%")
    acids_g_l: Optional[float] = Field(alias="Hapot g/l", default=None)
    sugar_g_l: Optional[float] = Field(alias="Sokeri g/l", default=None)
    energy_kcal: Optional[float] = Field(alias="Energia kcal/100 ml", default=None)
    
    # Packaging
    package_type: str | None = Field(alias="Pakkaustyyppi")
    closure_type: Optional[str] = Field(alias="Suljentatyyppi", default=None)
    ean: Optional[str] = Field(alias="EAN", default=None)

    # Description and flavor
    description: str = Field(alias="Luonnehdinta", default="")
    grapes: Optional[str] = Field(alias="Rypäleet", default=None)
    notes: Optional[str] = Field(alias="Huomautus", default=None)

    @computed_field
    @property
    def image_link(self) -> str:
        return f"https://images.alko.fi/images/cs_srgb,f_auto,t_products/cdn/{self.product_id}/.jpg"

    @computed_field
    @property
    def link(self) -> str:
        return f"https://www.alko.fi/tuotteet/{self.product_id}/"
    
    model_config = pydantic.ConfigDict(populate_by_name=True)
