# Schema Design

## The Core Problem

How do you represent a document in a way that:
- An AI can extract data into it
- A human can review and edit it
- The system can render it back to prose

A document is just text - lines of content. But "line 47" means nothing to a user. They think in terms of meaningful concepts: "investment amount", "delivery date", "party name".

The solution: model documents as structured data with metadata, not raw text.

---

## Document Structure

Every document follows the same hierarchy:

```
Document Type
  └── Section
        └── Field
              └── Value + Metadata
```

**Document Type**: What kind of document this is. Defines which sections and fields exist. Examples: term sheet, NDA, employment contract, invoice.

**Section**: A logical grouping of related fields. Maps to how humans think about documents ("the payment terms", "the confidentiality section"). Sections are ordered and named.

**Field**: A single piece of data. Has a name, type, and constraints. Can be required or optional. Each field extracts to exactly one value (though that value might be a list).

**Value + Metadata**: The actual content plus everything we know about it - where it came from, how confident we are, what alternatives exist.

This structure lets users interact at the right level of abstraction. They review "delivery date", not "line 47".

---

## Three Layers

The system uses three layers to transform source documents into a final output:

### Layer 1: Document Template Schema

Defines what a document type needs to contain. Built from domain knowledge (existing examples, industry standards, organization policies).

Each field has:
- **Name**: e.g., `payment_terms.due_date`
- **Type**: string, number, date, enum, etc.
- **Required/Optional**: whether generation can proceed without it
- **Default source**: which input typically provides this value

The schema is the contract. It says "a valid document of this type must have these fields".

### Layer 2: Extracted Fields

For each schema field, we extract candidate values from source documents. This is what users interact with in the review UI.

Each extracted field has:
- **value**: the actual content
- **source**: `{file, location}` - exactly where it came from
- **confidence**: 0.0 or 1.0 (binary)
- **conflicts**: alternative values from other sources
- **found**: whether a value was located
- **derived_from_policy**: true if using a default
- **reasoning**: why this value was chosen

This layer is the bridge. It connects raw source documents to structured data that users can understand and verify.

### Layer 3: Rendered Document

How extracted values become the final document text. A template with placeholders that get filled from confirmed field values.

Templates can include:
- Conditional sections (show/hide based on field values)
- Computed text (e.g., "non-participating" vs "fully participating" based on an enum)
- Formatting rules (dates, currency, percentages)

Each rendered section maps back to extracted fields, maintaining traceability.

---

## Scaling to Other Document Types

The architecture is document-agnostic. To add a new document type:

### 1. Define the Schema

Create a Pydantic model with sections and fields:

```python
class InvoiceSchema:
    vendor: VendorSection      # company name, address, tax ID
    client: ClientSection       # billing contact, PO number
    line_items: ItemsSection    # products/services, quantities, prices
    payment: PaymentSection     # terms, due date, payment methods
```

### 2. Write Extraction Prompts

For each section, create a prompt that tells the LLM what to extract:

```
Extract the PAYMENT section fields:
- due_date: when payment is due
- terms: payment terms (Net 30, etc.)
- methods: accepted payment methods
```

### 3. Create a Render Template

A markdown (or other format) template that uses the extracted fields:

```markdown
## Payment Terms
Payment is due on {due_date} ({terms}).
Accepted methods: {methods}
```

Further piece of work could be to use AI for generating this as part of a document tempalte generation process.

### 4. Register the Document Type

Add it to the system so users can select it at generation time.
**The extraction → review → finalize flow stays exactly the same.** That's the point. Users get a consistent experience regardless of document type.
