from pydantic import BaseModel, Field


class ImageMetadata(BaseModel):
    filename: str
    content_type: str
    size_bytes: int
    width: int | None = None
    height: int | None = None


class VisualElement(BaseModel):
    description: str
    location: str | None = None
    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )


class DocumentAnalysis(BaseModel):
    document_type: str | None = None
    title: str | None = None
    summary: str | None = None
    visible_text: list[str] = Field(default_factory=list)


class ProductAnalysis(BaseModel):
    product_name: str | None = None
    brand: str | None = None
    category: str | None = None
    visible_features: list[str] = Field(
        default_factory=list
    )


class UIAnalysis(BaseModel):
    application_or_website: str | None = None
    screen_description: str | None = None
    visible_components: list[str] = Field(
        default_factory=list
    )
    issues: list[str] = Field(
        default_factory=list
    )


class VisionAnalysis(BaseModel):
    summary: str
    visual_elements: list[VisualElement] = Field(
        default_factory=list
    )
    document_analysis: DocumentAnalysis | None = None
    product_analysis: ProductAnalysis | None = None
    ui_analysis: UIAnalysis | None = None
    answer: str | None = None
    uncertainty: list[str] = Field(
        default_factory=list
    )
    image_metadata: ImageMetadata | None = None


class ImageComparison(BaseModel):
    summary: str
    similarities: list[str] = Field(
        default_factory=list
    )
    differences: list[str] = Field(
        default_factory=list
    )
    uncertainty: list[str] = Field(
        default_factory=list
    )