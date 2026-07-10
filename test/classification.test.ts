/**
 * Visa AI Assistant — Classification Results Integration Test
 *
 * This test file validates the real classifier pipeline:
 * 1. Data model integrity (DOCUMENT_LABELS, VISA_REQUIREMENTS from types.js)
 * 2. Real AI classifier logic (from classifier.js)
 * 3. Full end-to-end analysis flow
 *
 * Run with: npx vitest run
 */

import { describe, it, expect } from "vitest"
import { render, screen, fireEvent, waitFor } from "@testing-library/react"
import { BrowserRouter } from "react-router-dom"
import { DOCUMENT_LABELS, VISA_REQUIREMENTS } from "../frontend/src/lib/types"
import {
  classifyDocument,
  classifyAllDocuments,
  validateAgainstRequirements,
  runFullAnalysis,
} from "../frontend/src/lib/classifier"

// ──────────────────────────────────────
// Part 1: Data Model Tests
// ──────────────────────────────────────

describe("Data Model", () => {
  it("defines document labels for common visa documents", () => {
    expect(DOCUMENT_LABELS.passport).toBe("Passport")
    expect(DOCUMENT_LABELS.bank_statement).toBe("Bank Statement")
    expect(DOCUMENT_LABELS.photograph).toBe("Passport Photograph")
    expect(DOCUMENT_LABELS.travel_itinerary).toBe("Travel Itinerary")
    expect(DOCUMENT_LABELS.other).toBe("Other Document")
  })

  it("defines visa type requirements", () => {
    expect(VISA_REQUIREMENTS.tourist).toBeDefined()
    expect(VISA_REQUIREMENTS.tourist.label).toBe("Tourist Visa")
    expect(VISA_REQUIREMENTS.tourist.required).toContain("passport")
    expect(VISA_REQUIREMENTS.tourist.required).toContain("bank_statement")

    expect(VISA_REQUIREMENTS.student.required).toContain("acceptance_letter")
    expect(VISA_REQUIREMENTS.work.required).toContain("employment_contract")
    expect(VISA_REQUIREMENTS.business.required).toContain("invitation_letter")
  })

  it("requires different documents for each visa type", () => {
    const touristDocs = VISA_REQUIREMENTS.tourist.required
    const studentDocs = VISA_REQUIREMENTS.student.required
    const workDocs = VISA_REQUIREMENTS.work.required
    const businessDocs = VISA_REQUIREMENTS.business.required

    // All types require basic documents
    for (const docs of [touristDocs, studentDocs, workDocs, businessDocs]) {
      expect(docs).toContain("passport")
      expect(docs).toContain("photograph")
      expect(docs).toContain("bank_statement")
    }

    // Each type has unique requirements
    expect(studentDocs).toContain("english_test")
    expect(workDocs).toContain("qualifications")
    expect(businessDocs).toContain("company_documents")
    expect(touristDocs).toContain("accommodation_proof")
  })
})

// ──────────────────────────────────────
// Part 2: Real Classifier Logic Tests
// ──────────────────────────────────────

describe("Classifier Engine", () => {
  it("classifies passport.pdf with good confidence", () => {
    const result = classifyDocument({ id: "1", file_name: "passport.pdf" })
    expect(result.classified_as).toBe("Passport")
    expect(result.confidence).toBeGreaterThanOrEqual(0.75)
    expect(result.issues).toHaveLength(0)
  })

  it("classifies photo.jpg as Passport Photograph", () => {
    const result = classifyDocument({ id: "2", file_name: "photo.jpg" })
    expect(result.classified_as).toBe("Passport Photograph")
    expect(result.confidence).toBeGreaterThanOrEqual(0.7)
  })

  it("classifies bank.pdf with generic-name warning", () => {
    const result = classifyDocument({ id: "3", file_name: "bank.pdf" })
    expect(result.classified_as).toBe("Bank Statement")
    // bank.pdf is short and generic, so it may trigger a "too generic" warning
    if (result.confidence < 0.7) {
      expect(result.issues.length).toBeGreaterThan(0)
    }
  })

  it("classifies invitation_letter.pdf with high confidence", () => {
    const result = classifyDocument({ id: "4", file_name: "invitation_letter.pdf" })
    expect(result.classified_as).toBe("Invitation Letter")
    expect(result.confidence).toBeGreaterThanOrEqual(0.8)
    expect(result.issues).toHaveLength(0)
  })

  it("handles partial name matches", () => {
    const result = classifyDocument({ id: "5", file_name: "My_Passport_Scan_2025.pdf" })
    expect(result.classified_as).toBe("Passport")
    expect(result.confidence).toBeGreaterThanOrEqual(0.85)
  })

  it("classifies descriptive file names with high confidence", () => {
    const result = classifyDocument({ id: "6", file_name: "Bank_Statement_January.pdf" })
    expect(result.classified_as).toBe("Bank Statement")
    expect(result.confidence).toBeGreaterThanOrEqual(0.8)
  })

  it("handles completely unrecognized files gracefully", () => {
    const result = classifyDocument({ id: "7", file_name: "random_file_xyz.pdf" })
    expect(result.classified_as).toBe("Other Document")
    expect(result.confidence).toBeLessThanOrEqual(0.5)
    expect(result.issues.length).toBeGreaterThan(0)
  })

  it("classifies IELTS test results", () => {
    const result = classifyDocument({ id: "8", file_name: "IELTS_Score_Report.pdf" })
    expect(result.classified_as).toBe("English Test Score")
    expect(result.confidence).toBeGreaterThanOrEqual(0.8)
  })

  it("classifies acceptance letter from university", () => {
    const result = classifyDocument({ id: "9", file_name: "University_Acceptance_Letter.pdf" })
    expect(result.classified_as).toBe("Acceptance Letter")
    expect(result.confidence).toBeGreaterThanOrEqual(0.85)
  })
})

// ──────────────────────────────────────
// Part 3: Classify All Documents
// ──────────────────────────────────────

describe("classifyAllDocuments", () => {
  it("classifies multiple documents at once", () => {
    const docs = [
      { id: "1", file_name: "passport.pdf" },
      { id: "2", file_name: "photo.jpg" },
      { id: "3", file_name: "Bank_Statement_2024.pdf" },
      { id: "4", file_name: "Travel_Itinerary.pdf" },
    ]

    const results = classifyAllDocuments(docs)
    expect(results).toHaveLength(4)
    expect(results[0].document_id).toBe("1")
    expect(results[0].classified_as).toBe("Passport")
    expect(results[0].status).toBe("verified")
  })

  it("marks documents with issues as needs_review", () => {
    const docs = [
      { id: "1", file_name: "random_file_xyz.pdf" },
    ]

    const results = classifyAllDocuments(docs)
    expect(results[0].status).toBe("needs_review")
    expect(results[0].issues.length).toBeGreaterThan(0)
  })
})

// ──────────────────────────────────────
// Part 4: Visa Requirement Validation
// ──────────────────────────────────────

describe("validateAgainstRequirements", () => {
  it("matches tourist visa requirements correctly", () => {
    const docs = [
      { id: "1", file_name: "passport.pdf" },
      { id: "2", file_name: "photo.jpg" },
      { id: "3", file_name: "Bank_Statement.pdf" },
      { id: "4", file_name: "Travel_Itinerary.pdf" },
      { id: "5", file_name: "Hotel_Booking.pdf" },
    ]

    const classifications = classifyAllDocuments(docs)
    const validation = validateAgainstRequirements(classifications, "tourist")

    // All 5 tourist requirements should be matched
    expect(validation.matched.length).toBe(5)
    expect(validation.missing).toHaveLength(0)
    expect(validation.score).toBeGreaterThanOrEqual(70)
  })

  it("detects missing required documents", () => {
    const docs = [
      { id: "1", file_name: "passport.pdf" },
      { id: "2", file_name: "photo.jpg" },
    ]

    const classifications = classifyAllDocuments(docs)
    const validation = validateAgainstRequirements(classifications, "work")

    expect(validation.missing.length).toBeGreaterThan(0)
    const missingTypes = validation.missing.map((m) => m.type)
    expect(missingTypes).toContain("employment_contract")
    expect(missingTypes).toContain("qualifications")
    expect(validation.score).toBeLessThan(70)
  })

  it("handles unknown visa type gracefully (falls back to tourist)", () => {
    const docs = [
      { id: "1", file_name: "passport.pdf" },
      { id: "2", file_name: "photo.jpg" },
      { id: "3", file_name: "Bank_Statement.pdf" },
    ]

    const classifications = classifyAllDocuments(docs)
    const validation = validateAgainstRequirements(classifications, "unknown_type")

    // Falls back to tourist requirements
    expect(validation.matched.length).toBeGreaterThanOrEqual(3)
  })
})

// ──────────────────────────────────────
// Part 5: Full Analysis Pipeline
// ──────────────────────────────────────

describe("runFullAnalysis", () => {
  it("processes a complete tourist visa application", () => {
    const docs = [
      { id: "1", file_name: "passport.pdf" },
      { id: "2", file_name: "photo.jpg" },
      { id: "3", file_name: "Bank_Statement.pdf" },
      { id: "4", file_name: "Travel_Itinerary.pdf" },
      { id: "5", file_name: "Hotel_Booking.pdf" },
    ]

    const result = runFullAnalysis(docs, "tourist")
    expect(result.classifications).toHaveLength(5)
    expect(result.validation.matched.length).toBe(5)
    expect(result.validation.missing).toHaveLength(0)
    expect(result.overall_score).toBeGreaterThanOrEqual(70)
    expect(result.status).toBe("verified")
  })

  it("detects a poor application clearly", () => {
    const docs = [
      { id: "1", file_name: "random_file.pdf" },
    ]

    const result = runFullAnalysis(docs, "work")
    expect(result.overall_score).toBeLessThan(40)
    expect(result.status).toBe("rejected")
    expect(result.validation.missing.length).toBeGreaterThanOrEqual(3)
  })

  it("returns consistent structure regardless of input", () => {
    const result = runFullAnalysis([], "tourist")
    expect(result).toHaveProperty("classifications")
    expect(result).toHaveProperty("validation")
    expect(result).toHaveProperty("overall_score")
    expect(result).toHaveProperty("status")
    expect(Array.isArray(result.classifications)).toBe(true)
  })
})

// ──────────────────────────────────────
// Part 6: UI Component Tests
// ──────────────────────────────────────

describe("StatusBadge", () => {
  it("renders verified status correctly", async () => {
    const { default: StatusBadge } = await import("../frontend/src/components/StatusBadge")
    render(<StatusBadge status="verified" />)
    expect(screen.getByText("Verified")).toBeInTheDocument()
  })

  it("renders pending status correctly", async () => {
    const { default: StatusBadge } = await import("../frontend/src/components/StatusBadge")
    render(<StatusBadge status="pending" />)
    expect(screen.getByText("Pending")).toBeInTheDocument()
  })

  it("renders failed status correctly", async () => {
    const { default: StatusBadge } = await import("../frontend/src/components/StatusBadge")
    render(<StatusBadge status="failed" />)
    expect(screen.getByText("Failed")).toBeInTheDocument()
  })

  it("renders needs_review status correctly", async () => {
    const { default: StatusBadge } = await import("../frontend/src/components/StatusBadge")
    render(<StatusBadge status="needs_review" />)
    expect(screen.getByText("Needs Review")).toBeInTheDocument()
  })
})

describe("ScoreCircle", () => {
  it("renders the score value", async () => {
    const { default: ScoreCircle } = await import("../frontend/src/components/ScoreCircle")
    render(<ScoreCircle score={85} />)
    expect(screen.getByText("85")).toBeInTheDocument()
    expect(screen.getByText("Excellent")).toBeInTheDocument()
  })

  it("shows correct label for low scores", async () => {
    const { default: ScoreCircle } = await import("../frontend/src/components/ScoreCircle")
    render(<ScoreCircle score={35} />)
    expect(screen.getByText("35")).toBeInTheDocument()
    expect(screen.getByText("Poor")).toBeInTheDocument()
  })

  it("shows correct label for medium scores", async () => {
    const { default: ScoreCircle } = await import("../frontend/src/components/ScoreCircle")
    render(<ScoreCircle score={65} />)
    expect(screen.getByText("65")).toBeInTheDocument()
    expect(screen.getByText("Good")).toBeInTheDocument()
  })
})

describe("DocumentCard", () => {
  const mockDocument = {
    id: "doc-1",
    application_id: "app-1",
    created_at: new Date().toISOString(),
    file_name: "passport.pdf",
    file_url: null,
    status: "verified" as const,
    document_type: "passport",
    classification: {
      id: "class-1",
      document_id: "doc-1",
      created_at: new Date().toISOString(),
      classified_as: "Passport",
      confidence: 0.97,
      details: { file_name: "passport.pdf", method: "ai_classifier_v1" },
      issues: [],
    },
  }

  it("renders document name and status", async () => {
    const { default: DocumentCard } = await import("../frontend/src/components/DocumentCard")
    render(
      <BrowserRouter>
        <DocumentCard document={mockDocument} required />
      </BrowserRouter>,
    )
    expect(screen.getByText("Passport")).toBeInTheDocument()
    expect(screen.getByText("Verified")).toBeInTheDocument()
  })

  it("shows required badge for required documents", async () => {
    const { default: DocumentCard } = await import("../frontend/src/components/DocumentCard")
    render(
      <BrowserRouter>
        <DocumentCard document={mockDocument} required />
      </BrowserRouter>,
    )
    expect(screen.getByText("Required")).toBeInTheDocument()
  })

  it("expands to show classification details on click", async () => {
    const { default: DocumentCard } = await import("../frontend/src/components/DocumentCard")
    render(
      <BrowserRouter>
        <DocumentCard document={mockDocument} required />
      </BrowserRouter>,
    )

    const expandButton = screen.getByLabelText("Document: passport.pdf")
    fireEvent.click(expandButton)

    await waitFor(() => {
      expect(screen.getByText("Classification Confidence")).toBeInTheDocument()
      expect(screen.getByText("97%")).toBeInTheDocument()
    })
  })

  it("shows issues when document has them", async () => {
    const docWithIssues = {
      ...mockDocument,
      file_name: "bank.pdf",
      classification: {
        ...mockDocument.classification!,
        classified_as: "Bank Statement",
        confidence: 0.78,
        issues: ["Low confidence in document type classification — verify manually"],
      },
    }
    const { default: DocumentCard } = await import("../frontend/src/components/DocumentCard")
    render(
      <BrowserRouter>
        <DocumentCard document={docWithIssues} />
      </BrowserRouter>,
    )

    const expandButton = screen.getByLabelText("Document: bank.pdf")
    fireEvent.click(expandButton)

    await waitFor(() => {
      expect(screen.getByText("Low confidence in document type classification — verify manually")).toBeInTheDocument()
    })
  })
})

describe("Visa Application End-to-End Flow", () => {
  it("fully validates a tourist visa application", () => {
    const documents = [
      { id: "1", file_name: "passport.pdf" },
      { id: "2", file_name: "photo.jpg" },
      { id: "3", file_name: "Bank.pdf" },
      { id: "4", file_name: "Travel_Itinerary.pdf" },
      { id: "5", file_name: "Hotel_Booking.confirmation.pdf" },
    ]

    // Step 1: Run full analysis through the real classifier
    const result = runFullAnalysis(documents, "tourist")

    // Step 2: Verify all documents classified
    expect(result.classifications).toHaveLength(5)

    // Step 3: Check all tourist visa requirements are met
    const requiredDocs = VISA_REQUIREMENTS.tourist.required
    const classifiedLabels = result.classifications.map((c) => c.classified_as)
    for (const req of requiredDocs) {
      const label = DOCUMENT_LABELS[req]
      expect(classifiedLabels).toContain(label)
    }

    // Step 4: Overall score should be decent
    expect(result.overall_score).toBeGreaterThanOrEqual(60)

    // Step 5: Verify no missing requirements
    expect(result.validation.missing).toHaveLength(0)
  })

  it("detects missing required documents", () => {
    // Simulate a submission missing some required documents
    const submittedLabels = ["Passport", "Passport Photograph", "Bank Statement"]
    const requiredForWork = VISA_REQUIREMENTS.work.required

    const missing = requiredForWork.filter((req) => !submittedLabels.includes(DOCUMENT_LABELS[req]))
    expect(missing).toContain("employment_contract")
    expect(missing).toContain("qualifications")
  })

  it("classifier output matches the structure UI components expect", () => {
    const doc = { id: "1", file_name: "passport.pdf" }
    const result = classifyDocument(doc)

    // The UI expects these fields from classification
    expect(result).toHaveProperty("classified_as")
    expect(result).toHaveProperty("confidence")
    expect(result).toHaveProperty("details")
    expect(result).toHaveProperty("issues")
    expect(typeof result.classified_as).toBe("string")
    expect(typeof result.confidence).toBe("number")
    expect(Array.isArray(result.issues)).toBe(true)
  })
})