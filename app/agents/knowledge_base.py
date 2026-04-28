"""
knowledge_base.py
─────────────────
RAG Knowledge Base for Insurance Hub.
Uses ChromaDB (local, no server needed) + sentence-transformers embeddings.
Stores India-specific insurance knowledge for precise retrieval.

Directory: app/agents/knowledge_base.py
"""

import os

# ── ChromaDB client (lazy init) ───────────────────────────────
_chroma_client     = None
_collection        = None
_embedding_fn      = None
DB_PATH            = "./chroma_insurance_db"


# ═══════════════════════════════════════════════════════════════
# INDIA-SPECIFIC INSURANCE KNOWLEDGE BASE
# ═══════════════════════════════════════════════════════════════
INSURANCE_KNOWLEDGE = [

    # ── HEALTH INSURANCE ──────────────────────────────────────
    {
        "id": "health_001",
        "text": (
            "Health insurance waiting period in India: "
            "Most policies impose a 30-day initial waiting period before any claims. "
            "Pre-existing diseases (PED) carry a 2-4 year waiting period depending on insurer. "
            "Maternity benefits have a 9-month to 2-year waiting period. "
            "Critical illness riders have a 90-day survival clause before payout."
        ),
        "metadata": {"type": "Health Insurance", "topic": "waiting_period", "market": "India"}
    },
    {
        "id": "health_002",
        "text": (
            "Cashless hospitalization in India: "
            "Available at network hospitals empanelled by the insurer's TPA (Third Party Administrator). "
            "Star Health covers 14,000+ hospitals; HDFC Ergo covers 13,000+; Niva Bupa covers 10,000+. "
            "Pre-authorization required 48-72 hours in advance for planned procedures. "
            "Emergency cashless is approved within 4-6 hours. "
            "Documents required: health card, photo ID, policy number."
        ),
        "metadata": {"type": "Health Insurance", "topic": "cashless", "market": "India"}
    },
    {
        "id": "health_003",
        "text": (
            "Health insurance No Claim Bonus (NCB) in India: "
            "NCB rewards policyholders for claim-free years with increased sum insured or premium discounts. "
            "Typical NCB: 5-50% increase in sum insured per claim-free year. "
            "Star Health offers 10% NCB; HDFC Ergo offers up to 50% NCB. "
            "NCB resets to zero after a claim is made in most policies. "
            "Some insurers offer NCB protection rider to preserve bonus after one claim."
        ),
        "metadata": {"type": "Health Insurance", "topic": "ncb", "market": "India"}
    },
    {
        "id": "health_004",
        "text": (
            "Health insurance premium ranges in India (2025-26): "
            "Individual 5 lakh cover, age 25-35: Rs 6,000-12,000 per year. "
            "Individual 10 lakh cover, age 25-35: Rs 10,000-18,000 per year. "
            "Family floater 5 lakh for 4 members: Rs 15,000-28,000 per year. "
            "Family floater 10 lakh for 4 members: Rs 20,000-40,000 per year. "
            "Senior citizen policies (60+): Rs 25,000-80,000 per year for 5 lakh cover. "
            "Top insurers: Star Health, Niva Bupa, HDFC Ergo, Care Health, Aditya Birla Health."
        ),
        "metadata": {"type": "Health Insurance", "topic": "premium", "market": "India"}
    },
    {
        "id": "health_005",
        "text": (
            "Health insurance tax benefits under Section 80D in India: "
            "Self and family (below 60 years): deduction up to Rs 25,000 per year. "
            "If policyholder is senior citizen (60+): deduction up to Rs 50,000. "
            "Additional Rs 25,000 for parents below 60; Rs 50,000 if parents are senior citizens. "
            "Maximum total deduction possible: Rs 1,00,000 per year. "
            "GST of 18% is charged on health insurance premiums and is not tax deductible."
        ),
        "metadata": {"type": "Health Insurance", "topic": "tax_benefit", "market": "India"}
    },
    {
        "id": "health_006",
        "text": (
            "Family floater health insurance in India: "
            "A single policy covers the entire family under one sum insured. "
            "All members can utilize the total sum insured but cannot exceed it collectively. "
            "More cost-effective than individual policies for families with healthy members. "
            "Risk: if one member makes a large claim, others have reduced coverage. "
            "Suitable for families where all members are below 45 and in good health. "
            "Premium is based on the oldest and highest-risk member in the family."
        ),
        "metadata": {"type": "Health Insurance", "topic": "family_floater", "market": "India"}
    },
    {
        "id": "health_007",
        "text": (
            "IRDAI regulations for health insurance in India: "
            "Insurers cannot deny renewal on grounds of health condition. "
            "Standard health insurance product Arogya Sanjeevani is available across all insurers. "
            "Moratorium period: after 8 continuous years, no pre-existing disease exclusion applies. "
            "Free-look period: 15 days to review and cancel for full refund. "
            "Portability rights: switch insurer while retaining NCB and waiting period credits."
        ),
        "metadata": {"type": "Health Insurance", "topic": "irdai_regulations", "market": "India"}
    },
    {
        "id": "car_008",
        "text": "To file a car insurance claim, you must first register the claim immediately via a 24x7 toll-free number, the IL Take Care app, or SMS [1]. You need to submit your claim by providing your policy cover note, vehicle chassis/registration number, and incident details [1]. For vehicle damage, you can complete an 'Instaspect' live video survey on the app before uploading the necessary supporting documents for assessment [1].",
        "metadata": {"type": "Car Insurance", "topic": "claim_process", "market": "India"}
    },
    {
        "id": "car_009",
        "text": "Filing a car insurance reimbursement claim requires the original claim form with an NEFT mandate, a copy of the Registration Certificate (RC), and a copy of the driver's license at the time of the accident [2]. You must also provide a copy of the policy, a certified officially valid document with a PAN card/Form 60, garage estimate, repair invoice, cancelled cheque, and an FIR or police report if applicable [3].",
        "metadata": {"type": "Car Insurance", "topic": "reimbursement_documents", "market": "India"}
    },
    {
        "id": "car_010",
        "text": "For total loss and net salvage car insurance claims, the required documents include the original RC, original policy schedule, and three signed copies of Form 28, 29 & 30 [2]. Additionally, you must submit an indemnity bond, PAN card copy, FIR, NEFT form with a cancelled cheque, and a No Objection Certificate (NOC) with Form 16 if the vehicle was purchased on a loan [2].",
        "metadata": {"type": "Car Insurance", "topic": "total_loss_documents", "market": "India"}
    },
    {
        "id": "car_011",
        "text": "For extended warranty car insurance claims, you are required to submit regular service and maintenance history records [2]. You must also provide the exact reading of the Speedometer or Odometer [3].",
        "metadata": {"type": "Car Insurance", "topic": "extended_warranty_documents", "market": "India"}
    },
    {
        "id": "broker_012",
        "text": "In India, an applicant can register as one of the following categories of insurance brokers: direct broker (life, general, or life & general), reinsurance broker, or composite broker [4]. The minimum capital requirement to act as an insurance broker is Rs. 75 Lakh for direct brokers, Rs. 4 Crore for reinsurance brokers, and Rs. 5 Crore for composite brokers [5].",
        "metadata": {"type": "Insurance Broker", "topic": "registration_and_capital", "market": "India"}
    },
    {
        "id": "broker_013",
        "text": "Insurance brokers are required to maintain a minimum net-worth at all times, which is Rs. 50 Lakh for a direct broker and 50% of the minimum capital requirement for reinsurance and composite brokers [6]. Additionally, brokers must keep a deposit in a scheduled bank equivalent to Rs. 10 Lakhs for a direct broker, or 10% of the minimum capital for a reinsurance or composite broker, which cannot be released without the Authority's written permission [7, 8].",
        "metadata": {"type": "Insurance Broker", "topic": "net_worth_and_deposit", "market": "India"}
    },

    # ── TERM INSURANCE ────────────────────────────────────────
    {
        "id": "term_001",
        "text": (
            "Term insurance coverage calculation in India: "
            "Ideal coverage is 10-15 times annual income. "
            "Annual income Rs 8 lakh: recommended cover Rs 80 lakh to Rs 1.2 crore. "
            "Annual income Rs 15 lakh: recommended cover Rs 1.5-2.25 crore. "
            "Additional cover for outstanding loans: home loan, car loan, personal loan balances. "
            "Consider inflation: a Rs 1 crore cover today equals Rs 54 lakh in purchasing power after 20 years at 3% inflation."
        ),
        "metadata": {"type": "Term Insurance", "topic": "coverage", "market": "India"}
    },
    {
        "id": "term_002",
        "text": (
            "Term insurance premium ranges in India (2025-26): "
            "Rs 1 crore cover, male non-smoker aged 25: Rs 8,000-12,000 per year for 30-year term. "
            "Rs 1 crore cover, male non-smoker aged 30: Rs 10,000-16,000 per year. "
            "Rs 1 crore cover, male non-smoker aged 35: Rs 14,000-22,000 per year. "
            "Women get 10-15% lower premiums than men of same age. "
            "Smokers pay 50-100% higher premiums. "
            "Online plans are 30-40% cheaper than offline agent-sold plans."
        ),
        "metadata": {"type": "Term Insurance", "topic": "premium", "market": "India"}
    },
    {
        "id": "term_003",
        "text": (
            "Term insurance claim settlement ratio (CSR) of top Indian insurers: "
            "Max Life Insurance: 99.51% CSR (highest). "
            "HDFC Life Insurance: 99.45% CSR. "
            "Tata AIA Life: 99.01% CSR. "
            "LIC of India: 98.62% CSR. "
            "ICICI Prudential Life: 97.90% CSR. "
            "SBI Life Insurance: 97.05% CSR. "
            "CSR above 95% is considered good. Always check CSR before buying term insurance."
        ),
        "metadata": {"type": "Term Insurance", "topic": "claim_settlement", "market": "India"}
    },
    {
        "id": "term_004",
        "text": (
            "Term insurance riders available in India: "
            "Critical Illness Rider: lump sum payout on diagnosis of 34-64 diseases; costs 15-25% extra premium. "
            "Accidental Death Benefit (ADB): pays additional 1-2x sum assured on accidental death. "
            "Waiver of Premium (WOP): future premiums waived on total permanent disability. "
            "Income Benefit Rider: monthly income to family instead of lump sum. "
            "Return of Premium (RoP): all premiums returned if policyholder survives term (30-40% higher premium)."
        ),
        "metadata": {"type": "Term Insurance", "topic": "riders", "market": "India"}
    },
    {
        "id": "term_005",
        "text": (
            "Term insurance claim process in India: "
            "Step 1: Intimate insurer via online portal, toll-free number, or nearest branch. "
            "Step 2: Submit claim form, original death certificate, original policy document. "
            "Step 3: Additional documents: ID proof of nominee, bank account proof, medical records. "
            "Step 4: For accidental death: FIR copy, post-mortem report, driving licence if applicable. "
            "Step 5: Insurer must settle or repudiate within 30 days of receiving all documents (IRDAI mandate). "
            "Early claim (within 3 years): requires additional investigation by insurer."
        ),
        "metadata": {"type": "Term Insurance", "topic": "claim_process", "market": "India"}
    },
    {
        "id": "term_006",
        "text": (
            "Term insurance tax benefits in India: "
            "Premium paid qualifies for deduction under Section 80C up to Rs 1.5 lakh per year. "
            "Death benefit received by nominee is fully tax-exempt under Section 10(10D). "
            "Critical illness rider payout may be taxable if premium exceeds 10% of sum assured. "
            "GST of 18% on term insurance premiums is not tax deductible. "
            "Return of Premium plans: maturity proceeds are tax-exempt under Section 10(10D)."
        ),
        "metadata": {"type": "Term Insurance", "topic": "tax_benefit", "market": "India"}
    },

    # ── VEHICLE INSURANCE ─────────────────────────────────────
    {
        "id": "vehicle_001",
        "text": (
            "Vehicle insurance IDV (Insured Declared Value) in India: "
            "IDV is the current market value of the vehicle minus depreciation. "
            "Depreciation schedule per IRDAI: 0-6 months: 5%; 6-12 months: 15%; 1-2 years: 20%; 2-3 years: 30%; 3-4 years: 40%; 4-5 years: 50%. "
            "Higher IDV = higher premium but better compensation on total loss or theft. "
            "Do not undervalue IDV to save premium; reduces claim payout proportionally. "
            "Vehicles older than 5 years: IDV agreed between insurer and insured."
        ),
        "metadata": {"type": "Vehicle Insurance", "topic": "idv", "market": "India"}
    },
    {
        "id": "vehicle_002",
        "text": (
            "Vehicle insurance No Claim Bonus (NCB) in India: "
            "NCB discount on Own Damage (OD) premium: "
            "1 claim-free year: 20% discount. "
            "2 claim-free years: 25% discount. "
            "3 claim-free years: 35% discount. "
            "4 claim-free years: 45% discount. "
            "5+ claim-free years: 50% discount (maximum). "
            "NCB is transferable when switching insurers — obtain NCB certificate. "
            "NCB resets to 0% after any claim; filing small claims loses NCB worth more than repair cost."
        ),
        "metadata": {"type": "Vehicle Insurance", "topic": "ncb", "market": "India"}
    },
    {
        "id": "vehicle_003",
        "text": (
            "Zero depreciation (nil dep) add-on for vehicle insurance in India: "
            "Standard policy deducts depreciation on parts during claim: "
            "50% depreciation on rubber, plastic, nylon, tyres. "
            "30% on fibre glass parts. "
            "Zero dep add-on pays full repair cost without depreciation deduction. "
            "Cost: typically 15-20% extra on OD premium. "
            "Highly recommended for vehicles under 5 years old. "
            "Usually available for vehicles up to 7-10 years old. "
            "Most insurers allow 2 claims per year with zero dep rider."
        ),
        "metadata": {"type": "Vehicle Insurance", "topic": "zero_dep", "market": "India"}
    },
    {
        "id": "vehicle_004",
        "text": (
            "Mandatory third-party vehicle insurance in India: "
            "Compulsory under the Motor Vehicles Act 1988 — driving without it is a criminal offense. "
            "Penalty for violation: fine up to Rs 2,000 and/or 3 months imprisonment for first offense. "
            "Third-party premium is fixed by IRDAI annually — same across all insurers. "
            "Third-party premium for private cars (above 1500cc): Rs 3,221 per year. "
            "Covers: death or injury to third parties, property damage up to Rs 7.5 lakh. "
            "Does NOT cover damage to own vehicle."
        ),
        "metadata": {"type": "Vehicle Insurance", "topic": "third_party", "market": "India"}
    },
    {
        "id": "vehicle_005",
        "text": (
            "Top vehicle insurance providers in India and their cashless garage networks: "
            "Tata AIG: 7,500+ cashless garages across India. "
            "HDFC Ergo: 6,800+ cashless garages. "
            "Bajaj Allianz: 4,000+ cashless garages. "
            "ICICI Lombard: 5,600+ cashless garages. "
            "Reliance General: 3,500+ cashless garages. "
            "Always choose insurer with wide network in your city. "
            "Check cashless garage locator on insurer website before purchasing."
        ),
        "metadata": {"type": "Vehicle Insurance", "topic": "cashless_garages", "market": "India"}
    },
    {
        "id": "vehicle_006",
        "text": (
            "Vehicle insurance claim process in India: "
            "Step 1: Inform insurer immediately via app, website, or 24x7 helpline. "
            "Step 2: For accident: do not move vehicle until surveyor arrives or take photos. "
            "Step 3: File FIR at nearest police station for theft, third-party injury, or major accidents. "
            "Step 4: Insurer appoints surveyor within 24-48 hours. "
            "Step 5: For cashless: vehicle repaired at network garage; insurer pays directly. "
            "Step 6: For reimbursement: get vehicle repaired, submit original bills, receive payment in 7-15 days. "
            "Documents needed: claim form, driving licence, RC book, policy copy, FIR (if applicable)."
        ),
        "metadata": {"type": "Vehicle Insurance", "topic": "claim_process", "market": "India"}
    },

    # ── GENERAL INSURANCE KNOWLEDGE ───────────────────────────
    {
        "id": "general_001",
        "text": (
            "IRDAI (Insurance Regulatory and Development Authority of India) overview: "
            "IRDAI is the statutory body regulating the insurance sector in India. "
            "Established under IRDAI Act 1999. "
            "Headquarters: Hyderabad, Telangana. "
            "Key functions: licensing insurers, protecting policyholder interests, setting regulations. "
            "IRDAI Bima Bharosa grievance portal for complaints: https://bimabharosa.irdai.gov.in. "
            "Ombudsman offices in 17 cities handle disputes up to Rs 30 lakh. "
            "Free look period mandate: 15 days for regular policies, 30 days for distance marketing."
        ),
        "metadata": {"type": "General", "topic": "irdai", "market": "India"}
    },
    {
        "id": "general_002",
        "text": (
            "Insurance premium payment modes in India: "
            "Annual: lowest effective premium, best value. "
            "Semi-annual: slight loading of 2-3% over annual. "
            "Quarterly: loading of 3-5% over annual. "
            "Monthly: highest loading of 5-8% over annual; convenient but expensive. "
            "ECS/NACH mandate: automatic debit for regular premium payment. "
            "Grace period: 15 days for monthly policies, 30 days for other modes. "
            "Policy lapses if premium not paid within grace period."
        ),
        "metadata": {"type": "General", "topic": "premium_payment", "market": "India"}
    },

    # ══════════════════════════════════════════════════════════════
    # NEW CHUNKS — IRDAI Ind AS 2026 REGULATIONS
    # Source 1: IRDAI Circular Ref IRDAI/IFRS/CIR/MISC/45/4/2026 dated 1st April 2026
    # Source 2: IRDAI Press Release dated 30th March 2026 — 135th Authority Meeting
    # ══════════════════════════════════════════════════════════════

    # ── HEALTH INSURANCE — IRDAI Ind AS 2026 ─────────────────
    {
        "id": "health_008",
        "text": (
            "IRDAI Ind AS financial reporting for health insurers from April 2026: "
            "All Stand Alone Health Insurers (SAHIs) must prepare financial statements "
            "under Indian Accounting Standards (Ind AS) from 1st April 2026, mandated by "
            "IRDAI (Actuarial, Finance and Investment Functions of Insurers) (Amendment) Regulations 2026 "
            "approved at the 135th Authority Meeting on 30th March 2026. "
            "Health insurers must submit quarterly Financial Statements under Ind AS (Schedule IIA) "
            "alongside parallel Financial Information under the existing framework (Schedule II) for two years. "
            "First three quarters are subject to limited review by a Chartered Accountant. "
            "Annual statements are subject to full audit under Insurance Act 1938 and Companies Act 2013."
        ),
        "metadata": {"type": "Health Insurance", "topic": "irdai_ind_as_2026", "market": "India"}
    },
    {
        "id": "health_009",
        "text": (
            "IRDAI Ind AS policyholder fund segregation for health insurers — April 2026: "
            "As per IRDAI Circular IRDAI/IFRS/CIR/MISC/45/4/2026, segregation of policyholder and "
            "shareholder funds must continue under Section 11 of the Insurance Act 1938 "
            "even after adoption of Ind AS by health insurers. "
            "Health insurers must present policyholder and shareholder fund items separately in "
            "Financial Statements under Ind AS as per Schedule IIA of the Regulations. "
            "This ensures policyholder interests are protected and funds are not co-mingled with "
            "shareholder capital under the new accounting framework. "
            "Segregation must be maintained in accordance with the Master Circular on Actuarial, "
            "Finance and Investment Functions of Insurers 2024."
        ),
        "metadata": {"type": "Health Insurance", "topic": "policyholder_fund_segregation", "market": "India"}
    },
    {
        "id": "health_010",
        "text": (
            "IRDAI forbearance provision for health insurers under Ind AS 2026: "
            "Health insurers facing transition challenges can apply for one-year forbearance "
            "by submitting an application to IRDAI on or before 30th April 2026. "
            "Application must include a Board-approved action plan with monthly milestones, "
            "system readiness timelines, actuarial and finance function preparedness status, "
            "and a governance framework for overseeing the Ind AS transition. "
            "During forbearance, insurers must still prepare Ind AS proforma statements "
            "(Financial Information under Schedule IIA) and submit monthly progress reports to IRDAI. "
            "Financial Statements during forbearance period are prepared under Schedule II (existing framework). "
            "Financial Information for all four quarters during forbearance must be subject to "
            "limited review by a CA and certification from an Independent Actuary."
        ),
        "metadata": {"type": "Health Insurance", "topic": "ind_as_forbearance", "market": "India"}
    },

    # ── TERM INSURANCE — IRDAI Ind AS 2026 ───────────────────
    {
        "id": "term_007",
        "text": (
            "IRDAI Ind AS financial reporting for life and term insurers from April 2026: "
            "All Life Insurers offering term insurance must prepare financial statements "
            "under Indian Accounting Standards (Ind AS) effective 1st April 2026, as mandated by "
            "IRDAI (Amendment) Regulations 2026 approved on 30th March 2026. "
            "Term insurers must follow Ind AS 117 (Insurance Contracts) for recognition, measurement, "
            "presentation and disclosure of insurance contract liabilities including term policies. "
            "Discounting of insurance contract liabilities must use the risk-free rate derived from "
            "Government of India securities zero-coupon yield curve published by CCIL "
            "(Clearing Corporation of India Limited) or any other source specified by IRDAI."
        ),
        "metadata": {"type": "Term Insurance", "topic": "irdai_ind_as_2026", "market": "India"}
    },
    {
        "id": "term_008",
        "text": (
            "IRDAI Ind AS actuarial and solvency framework for term insurance — 2026: "
            "As per IRDAI Circular IRDAI/IFRS/CIR/MISC/45/4/2026, the adoption of Ind AS does NOT "
            "alter the basis of actuarial investigation, determination of surplus, or solvency assessment "
            "for life and term insurers. "
            "Actuarial investigation and actuary report submission continues under Section 13 of the "
            "Insurance Act 1938 and Schedule I of the Regulations. "
            "Determination and distribution of surplus is governed by Section 49 of the Insurance Act 1938. "
            "Solvency margin maintenance continues under Sections 64V and 64VA of the Insurance Act 1938. "
            "Insurers must ensure that Ind AS adoption does not, by itself, alter the basis of "
            "actuarial investigation or solvency assessment — these remain unchanged."
        ),
        "metadata": {"type": "Term Insurance", "topic": "ind_as_actuarial_solvency", "market": "India"}
    },
    {
        "id": "term_009",
        "text": (
            "IRDAI parallel reporting requirement for term insurance companies — 2026: "
            "All life insurers offering term plans must undertake parallel reporting for two years "
            "from 1st April 2026 as per IRDAI (Amendment) Regulations 2026. "
            "This means submitting both: "
            "Financial Statements under Ind AS (Schedule IIA) — new framework; and "
            "Financial Information under existing framework (Schedule II) — old framework. "
            "Both must be submitted quarterly and disclosed on the insurer website. "
            "For listed term insurers, SEBI timelines for Financial Statement disclosures continue to apply. "
            "For financial year 2026-27, first three quarters must be submitted within three months "
            "from the end of each respective quarter. "
            "Reconciliation between Financial Statements and Financial Information must be provided per Ind AS 101."
        ),
        "metadata": {"type": "Term Insurance", "topic": "ind_as_parallel_reporting", "market": "India"}
    },

    # ── VEHICLE INSURANCE — IRDAI Ind AS 2026 ────────────────
    {
        "id": "vehicle_007",
        "text": (
            "IRDAI Ind AS financial reporting for general and vehicle insurers from April 2026: "
            "All General Insurers including motor and vehicle insurance providers must prepare "
            "financial statements under Indian Accounting Standards (Ind AS) from 1st April 2026, "
            "per IRDAI Amendment Regulations 2026 approved at the 135th Authority Meeting on 30th March 2026. "
            "Vehicle insurers must implement Ind AS 117 for insurance contract liabilities. "
            "Quarterly Financial Statements (Schedule IIA — Ind AS) and Financial Information "
            "(Schedule II — existing) must both be prepared, submitted to IRDAI, and "
            "disclosed on the insurer website for two years (parallel reporting period). "
            "First three quarters subject to limited review; annual statements subject to full audit."
        ),
        "metadata": {"type": "Vehicle Insurance", "topic": "irdai_ind_as_2026", "market": "India"}
    },
    {
        "id": "vehicle_008",
        "text": (
            "IRDAI Ind AS investment and expense regulations for vehicle insurers — 2026: "
            "As per IRDAI Circular IRDAI/IFRS/CIR/MISC/45/4/2026, all regulations and Master Circulars "
            "pertaining to Investment functions, Expenses of Management, Submission of returns, and "
            "Public Disclosures for general and vehicle insurers continue to be governed by Schedule II "
            "of the Regulations even after Ind AS adoption. "
            "Vehicle insurers must consistently apply Schedule II principles while complying with "
            "investment and expense management regulatory frameworks, unless specifically modified "
            "or clarified by the Competent Authority. "
            "Any clarifications on Ind AS implementation can be directed to indas-team@irdai.gov.in."
        ),
        "metadata": {"type": "Vehicle Insurance", "topic": "ind_as_investment_expenses", "market": "India"}
    },

    # ── GENERAL INSURANCE — IRDAI Ind AS 2026 ────────────────
    {
        "id": "general_003",
        "text": (
            "IRDAI introduces Indian Accounting Standards (Ind AS) for insurance sector — 2026: "
            "IRDAI approved the Insurance Regulatory and Development Authority of India (Actuarial, "
            "Finance and Investment Functions of Insurers) (Amendment) Regulations 2026 at its "
            "135th Authority Meeting on 30th March 2026. "
            "Ind AS is mandatory for ALL categories of insurers from 1st April 2026: "
            "Life Insurers, General Insurers, Stand Alone Health Insurers (SAHIs), and Reinsurers. "
            "Objective: enhance consistency, transparency, and comparability in financial reporting "
            "across the Indian insurance sector in alignment with globally accepted accounting standards. "
            "ICAI (Institute of Chartered Accountants of India) and IAI (Institute of Actuaries of India) "
            "have expressed readiness to support insurers and auditing professionals in this transition."
        ),
        "metadata": {"type": "General", "topic": "irdai_ind_as_introduction_2026", "market": "India"}
    },
    {
        "id": "general_004",
        "text": (
            "IRDAI Ind AS Circular IRDAI/IFRS/CIR/MISC/45/4/2026 — key clarifications for all insurers: "
            "Issued 1st April 2026 under Section 34 of the Insurance Act 1938 and Section 14 of IRDA Act 1999. "
            "Key clarifications: "
            "1. Financial Statements under Ind AS (Schedule IIA) are the basis of financial reporting from April 2026. "
            "2. Parallel reporting of Ind AS statements and existing framework statements mandatory for two years. "
            "3. Both Financial Statements and Financial Information submitted quarterly and published on insurer website. "
            "4. First three quarters subject to limited review by CA; annual statements subject to full audit. "
            "5. Forbearance of one year available for insurers facing transition challenges — apply by 30th April 2026. "
            "6. Contact for Ind AS implementation clarifications: indas-team@irdai.gov.in."
        ),
        "metadata": {"type": "General", "topic": "irdai_ind_as_circular_2026", "market": "India"}
    },
    {
        "id": "general_005",
        "text": (
            "IRDAI Ind AS discount rate and independent validation for insurers — 2026: "
            "As per IRDAI Circular IRDAI/IFRS/CIR/MISC/45/4/2026: "
            "Discounting of insurance contract liabilities must be carried out per Ind AS 117 (Insurance Contracts). "
            "The risk-free rate for discounting shall be derived from Government of India securities "
            "using the zero-coupon yield curve published by CCIL (Clearing Corporation of India Limited) "
            "or any other source specified by IRDAI from time to time. "
            "Independent validation scope: The Competent Authority in consultation with the Joint Expert Group "
            "constituted under the Regulations will specify the scope and manner of independent validation "
            "of processes adopted for Ind AS implementation by all insurers."
        ),
        "metadata": {"type": "General", "topic": "irdai_ind_as_discount_rate", "market": "India"}
    },
    {
        "id": "general_006",
        "text": (
            "IRDAI Ind AS forbearance detailed steps for all insurers — 2026: "
            "Insurers seeking one-year forbearance from immediate Ind AS implementation must: "
            "Step 1: Submit application to IRDAI on or before 30th April 2026. "
            "Step 2: Include a Board-approved action plan with the application. "
            "Step 3: Action plan must specify monthly milestones, system and data readiness timelines, "
            "actuarial and finance function preparedness, and governance framework for transition oversight. "
            "Step 4: After forbearance is granted, submit monthly progress reports to IRDAI showing "
            "milestone achievement status, key gaps identified, and remedial actions undertaken. "
            "Step 5: During forbearance, prepare Financial Statements under Schedule II (existing framework) "
            "AND Financial Information (Ind AS proforma) under Schedule IIA — both submitted quarterly. "
            "Financial Information during forbearance must be reviewed by CA and certified by Independent Actuary."
        ),
        "metadata": {"type": "General", "topic": "irdai_ind_as_forbearance_steps", "market": "India"}
    },
    {
        "id": "general_007",
        "text": (
            "IRDAI Ind AS transparency and policyholder protection goals — 2026: "
            "The adoption of Ind AS by all Indian insurers from April 2026 aims to: "
            "Enhance transparency in financial reporting across Life, General, Health, and Reinsurance sectors. "
            "Improve credibility and regulatory oversight of insurer financial health. "
            "Align Indian insurance financial reporting with globally accepted standards (aligned with IFRS 17). "
            "Safeguard policyholder interests through standardised, audited financial disclosures. "
            "Support development of a robust and globally aligned insurance ecosystem in India. "
            "The framework was developed after extensive stakeholder consultations including public comments "
            "on the Exposure Draft and engagement with insurers and industry professionals. "
            "Source: IRDAI Press Release dated 30th March 2026 — 135th Authority Meeting."
        ),
        "metadata": {"type": "General", "topic": "irdai_ind_as_goals_2026", "market": "India"}
    },
]


def _get_collection():
    """Lazy-initialize ChromaDB collection with sentence-transformer embeddings."""
    global _chroma_client, _collection, _embedding_fn

    if _collection is not None:
        return _collection

    try:
        import chromadb
        from chromadb.utils import embedding_functions

        # Free local embeddings — no API key needed
        _embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        _chroma_client = chromadb.PersistentClient(path=DB_PATH)
        _collection    = _chroma_client.get_or_create_collection(
            name="insurance_india",
            embedding_function=_embedding_fn
        )

        # Load knowledge base if empty
        if _collection.count() < len(INSURANCE_KNOWLEDGE):
            _load_knowledge_base()

        return _collection

    except ImportError:
        print("[RAG] ChromaDB/sentence-transformers not installed — RAG disabled.")
        return None
    except Exception as e:
        print(f"[RAG] Init error: {e}")
        return None


def _load_knowledge_base():
    """Load all insurance knowledge into ChromaDB."""
    collection = _collection
    existing_ids = set()

    try:
        existing = collection.get()
        existing_ids = set(existing["ids"])
    except Exception:
        pass

    new_docs = [
        doc for doc in INSURANCE_KNOWLEDGE
        if doc["id"] not in existing_ids
    ]

    if not new_docs:
        return

    collection.add(
        ids       = [d["id"]       for d in new_docs],
        documents = [d["text"]     for d in new_docs],
        metadatas = [d["metadata"] for d in new_docs]
    )
    print(f"[RAG] Loaded {len(new_docs)} knowledge chunks into ChromaDB.")


def retrieve_context(query: str, policy_type: str = None, n_results: int = 4) -> str:
    """
    Retrieve relevant insurance knowledge from ChromaDB.

    Args:
        query:       User's natural language question
        policy_type: Filter by policy type (Health/Term/Vehicle Insurance)
        n_results:   Number of chunks to retrieve

    Returns:
        Concatenated context string for the agent
    """
    collection = _get_collection()

    if collection is None:
        # Fallback: return empty — agents work without RAG
        return ""

    try:
        where_filter = None
        if policy_type and policy_type in ["Health Insurance", "Term Insurance", "Vehicle Insurance"]:
            where_filter = {"type": policy_type}

        results = collection.query(
            query_texts = [query],
            n_results   = n_results,
            where       = where_filter
        )

        docs = results.get("documents", [[]])[0]
        if not docs:
            return ""

        context = "\n\n---\n\n".join(docs)
        return context

    except Exception as e:
        print(f"[RAG] Retrieval error: {e}")
        return ""


def initialize_knowledge_base():
    """
    Call this on app startup to pre-load ChromaDB.
    Add to create_app() in __init__.py.
    """
    try:
        _get_collection()
        print("[RAG] Knowledge base ready.")
    except Exception as e:
        print(f"[RAG] Startup init failed: {e}")