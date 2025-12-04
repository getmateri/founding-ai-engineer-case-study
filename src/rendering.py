"""
Document Rendering

Converts extracted fields into the final term sheet markdown document.
Uses contract-style prose format (no tables).
"""

from datetime import datetime
from .schema import TermSheetData


TERM_SHEET_TEMPLATE = '''# TERM SHEET

## {round_type} FINANCING
## {company_name}

This Term Sheet summarizes the principal terms of the proposed investment in {company_name} (the "Company"). This Term Sheet is not a legally binding obligation except for the sections entitled "Confidentiality," "Exclusivity," and "Expenses," which shall be binding upon execution. Any other legally binding obligation will only be made pursuant to definitive agreements to be negotiated and executed by the parties.

---

## 1. OFFERING TERMS

**Issuer:** {company_name}, a {company_jurisdiction} corporation (the "Company").

**Founders:** {founders} (collectively, the "Founders").

**Investors:** {lead_investor} (the "Lead Investor"), together with other investors acceptable to the Company and the Lead Investor (collectively, the "Investors").

**Amount of Financing:** The Investors agree to invest {investment_amount} (the "Investment Amount") in the Company.

**Pre-Money Valuation:** The Company is valued at {pre_money_valuation} prior to the Investment (the "Pre-Money Valuation").

**Price Per Share:** Based on the Pre-Money Valuation, the price per share of the Security shall be {price_per_share} (the "Original Purchase Price").

**Type of Security:** The Investment shall be made in the form of {security_type} (the "Preferred Stock" or the "Security").

**Post-Closing Capitalization:** Upon completion of the financing, the Investors shall own approximately {target_ownership_pct} of the Company on a fully-diluted basis.

**Option Pool:** Prior to the closing, the Company shall reserve {option_pool_pct} of its fully-diluted capitalization for issuance to employees, directors, and consultants under the Company's equity incentive plan (the "Option Pool"). The Option Pool shall be created on a {option_pool_timing} basis.

---

## 2. RIGHTS AND PREFERENCES OF THE PREFERRED STOCK

**Liquidation Preference:** In the event of any liquidation, dissolution, or winding up of the Company, whether voluntary or involuntary, or any Deemed Liquidation Event (as defined below), the holders of the Preferred Stock shall be entitled to receive, prior and in preference to any distribution to the holders of Common Stock, an amount per share equal to {liquidation_preference_multiple} times the Original Purchase Price, plus any declared but unpaid dividends (the "Liquidation Preference").

{participation_clause}

**Dividends:** The holders of the Preferred Stock shall be entitled to receive {dividend_type} dividends at the rate of {dividend_rate_pct} per annum of the Original Purchase Price, payable when, as, and if declared by the Board of Directors. No dividends shall be paid on Common Stock unless and until dividends have been paid on the Preferred Stock.

**Anti-Dilution Protection:** The Preferred Stock shall have {anti_dilution_type} anti-dilution protection. In the event the Company issues additional equity securities at a purchase price less than the current conversion price of the Preferred Stock, the conversion price shall be adjusted according to the applicable formula.

**Conversion:** Each share of Preferred Stock shall be convertible, at the option of the holder, at any time, into shares of Common Stock at the then-applicable conversion rate (initially one-to-one, subject to adjustment for stock splits, dividends, and anti-dilution provisions).

**Automatic Conversion:** The Preferred Stock shall automatically convert into Common Stock upon (i) the closing of a firmly underwritten public offering with gross proceeds of at least $50,000,000 and a price per share of at least three times the Original Purchase Price, or (ii) the written consent of the holders of a majority of the outstanding Preferred Stock.

---

## 3. CORPORATE GOVERNANCE

**Board of Directors:** The Board of Directors shall consist of {board_seats_total} members. The Board composition shall be as follows: {board_seats_investor} director(s) designated by the Lead Investor, {board_seats_founder} director(s) designated by the Founders{board_independent_clause}.

{board_observer_clause}

{quorum_clause}

**Protective Provisions:** For so long as any shares of Preferred Stock remain outstanding, the Company shall not, without the prior written consent of the holders of a majority of the Preferred Stock, voting as a separate class:

(a) Alter or change the rights, preferences, or privileges of the Preferred Stock;

(b) Increase or decrease the authorized number of shares of Common Stock or Preferred Stock;

(c) Create any new class or series of shares having rights, preferences, or privileges senior to or on parity with the Preferred Stock;

(d) Redeem or repurchase any shares of Common Stock or Preferred Stock (other than pursuant to equity incentive agreements with service providers);

(e) Declare or pay any dividend or make any distribution on any shares of Common Stock or Preferred Stock;

(f) Effect any merger, consolidation, or sale of all or substantially all of the Company's assets;

(g) Increase or decrease the authorized size of the Board of Directors;

(h) Incur indebtedness in excess of $250,000, other than trade payables incurred in the ordinary course of business;

(i) Enter into any transaction with any Founder, officer, or director, or any affiliate thereof, except for reasonable compensation and benefits approved by the Board.

**Pro-Rata Rights:** {pro_rata_clause}

**Drag-Along Rights:** If the Board of Directors, holders of a majority of the Preferred Stock, and holders of a majority of the Common Stock approve a sale of the Company, all stockholders shall be required to vote in favor of such transaction and to sell their shares on the same terms and conditions.

---

## 4. FOUNDER PROVISIONS

**Vesting:** All shares of Common Stock held by the Founders shall be subject to vesting over {vesting_period_months} months, with {vesting_cliff_months} months cliff vesting and {vesting_frequency} vesting thereafter. Upon any termination of a Founder's employment, the Company shall have the right to repurchase any unvested shares at the lower of cost or fair market value.

**Acceleration:** {acceleration_clause}

**Proprietary Information and Inventions Agreement:** Each Founder and key employee shall enter into a Proprietary Information and Inventions Assignment Agreement in a form acceptable to the Investors.

**Non-Competition:** Each Founder shall agree not to engage in any activity competitive with the Company during employment and for a period of {non_compete_months} months following termination of employment.

**Non-Solicitation:** Each Founder shall agree not to solicit or hire any employee of the Company during employment and for a period of {non_solicit_months} months following termination of employment.

---

## 5. TRANSACTION TERMS

**Exclusivity:** For a period of {exclusivity_days} days from the date this Term Sheet is signed, the Company and Founders agree not to solicit, encourage, negotiate, or accept any offer from any other party for the purchase of equity securities of the Company.

**Expenses:** The Company shall pay the reasonable legal fees and expenses of the Lead Investor in connection with the transactions contemplated by this Term Sheet, up to a maximum of {legal_fee_cap}.

**Expected Closing:** The parties shall use commercially reasonable efforts to close the transaction within {expected_closing_days} days of execution of this Term Sheet.

**Governing Law:** This Term Sheet and the definitive agreements shall be governed by and construed in accordance with the laws of the State of {governing_law}, without giving effect to conflict of laws principles.

**Confidentiality:** This Term Sheet and the terms contained herein are confidential and may not be disclosed to any third party without the prior written consent of the other parties, except to legal and financial advisors under a duty of confidentiality.

---

## 6. SIGNATURES

This Term Sheet is intended to be {binding_status} except for the provisions relating to Confidentiality, Exclusivity, and Expenses, which shall be legally binding upon execution by the parties.

{effective_date_clause}

**COMPANY:**

{company_name}


_______________________________
Name: {company_signatory_name}
Title: {company_signatory_title}
Date: _____________


**LEAD INVESTOR:**

{lead_investor}


_______________________________
Name: {investor_signatory_name}
Title: {investor_signatory_title}
Date: _____________

---

*This Term Sheet expires if not signed by both parties within 14 days of the date first written above.*
'''


def render_term_sheet(data: TermSheetData) -> str:
    """Render the term sheet markdown from extracted data"""
    
    def get_value(field, default="[To be provided]"):
        """Get field value or default"""
        if field and field.value:
            return field.value
        return default
    
    # Build conditional clauses
    
    # Participation clause
    participation_type = get_value(data.liquidation_terms.participation_type, "non-participating")
    if participation_type == "non-participating":
        participation_clause = "The Preferred Stock shall be non-participating. Upon a liquidation event, holders of Preferred Stock shall receive the greater of (i) the Liquidation Preference, or (ii) the amount they would receive if they converted to Common Stock immediately prior to the liquidation event."
    elif participation_type == "participating":
        participation_clause = "The Preferred Stock shall be fully participating. After payment of the Liquidation Preference, the remaining proceeds shall be distributed pro rata to the holders of Common Stock and Preferred Stock on an as-converted basis."
    else:
        participation_clause = f"The Preferred Stock shall be {participation_type}."
    
    # Board independent clause
    board_independent = get_value(data.governance.board_seats_independent, "0")
    if board_independent and board_independent != "0":
        board_independent_clause = f", and {board_independent} independent director(s) mutually agreed upon by the Company and the Investors"
    else:
        board_independent_clause = ""
    
    # Board observer clause
    if get_value(data.governance.board_observer_rights, "false").lower() == "true":
        board_observer_clause = "**Board Observer:** The Lead Investor shall have the right to appoint one representative to attend all meetings of the Board of Directors in a non-voting, observer capacity."
    else:
        board_observer_clause = ""
    
    # Quorum clause
    if get_value(data.governance.investor_consent_for_quorum, "false").lower() == "true":
        quorum_clause = "**Quorum:** The presence of the director designated by the Lead Investor shall be required to establish a quorum for any meeting of the Board of Directors."
    else:
        quorum_clause = ""
    
    # Pro-rata clause
    if get_value(data.governance.pro_rata_rights, "true").lower() == "true":
        pro_rata_clause = "Each Investor shall have the right to purchase its pro-rata share of any new securities issued by the Company (subject to customary exceptions), based on such Investor's ownership percentage on a fully-diluted basis."
    else:
        pro_rata_clause = "The Investors shall not have pro-rata rights in future financings."
    
    # Acceleration clause
    acceleration_type = get_value(data.founder_terms.acceleration_type, "none")
    if acceleration_type.lower() == "none":
        acceleration_clause = "There shall be no acceleration of vesting upon a change of control or termination event."
    elif "double" in acceleration_type.lower():
        acceleration_clause = "Upon a change of control followed by termination without cause or resignation for good reason within 12 months of such change of control, 100% of each Founder's unvested shares shall immediately vest (double-trigger acceleration)."
    elif "single" in acceleration_type.lower():
        acceleration_clause = "Upon a change of control, 100% of each Founder's unvested shares shall immediately vest (single-trigger acceleration)."
    else:
        acceleration_clause = f"Acceleration: {acceleration_type}"
    
    # Effective date clause
    effective_date = get_value(data.signatures.effective_date, None)
    if effective_date:
        effective_date_clause = f"**Effective Date:** {effective_date}"
    else:
        effective_date_clause = ""
    
    # Render template
    rendered = TERM_SHEET_TEMPLATE.format(
        # Parties
        company_name=get_value(data.parties.company_name),
        company_jurisdiction=get_value(data.parties.company_jurisdiction, "Delaware"),
        founders=get_value(data.parties.founders),
        lead_investor=get_value(data.parties.lead_investor),
        
        # Deal Economics
        round_type=get_value(data.deal_economics.round_type, "SERIES A").upper(),
        investment_amount=get_value(data.deal_economics.investment_amount),
        pre_money_valuation=get_value(data.deal_economics.pre_money_valuation),
        price_per_share=get_value(data.deal_economics.price_per_share, "TBD"),
        security_type=get_value(data.deal_economics.security_type, "Series A Preferred Stock"),
        target_ownership_pct=get_value(data.deal_economics.target_ownership_pct, "20%"),
        option_pool_pct=get_value(data.deal_economics.option_pool_pct, "15%"),
        option_pool_timing=get_value(data.deal_economics.option_pool_timing, "pre-money"),
        
        # Liquidation Terms
        liquidation_preference_multiple=get_value(data.liquidation_terms.liquidation_preference_multiple, "1"),
        participation_clause=participation_clause,
        dividend_type=get_value(data.liquidation_terms.dividend_type, "non-cumulative"),
        dividend_rate_pct=get_value(data.liquidation_terms.dividend_rate_pct, "6%"),
        anti_dilution_type=get_value(data.liquidation_terms.anti_dilution_type, "broad-based weighted average"),
        
        # Governance
        board_seats_total=get_value(data.governance.board_seats_total, "3"),
        board_seats_investor=get_value(data.governance.board_seats_investor, "1"),
        board_seats_founder=get_value(data.governance.board_seats_founder, "2"),
        board_independent_clause=board_independent_clause,
        board_observer_clause=board_observer_clause,
        quorum_clause=quorum_clause,
        pro_rata_clause=pro_rata_clause,
        
        # Founder Terms
        vesting_period_months=get_value(data.founder_terms.vesting_period_months, "48"),
        vesting_cliff_months=get_value(data.founder_terms.vesting_cliff_months, "12"),
        vesting_frequency=get_value(data.founder_terms.vesting_frequency, "monthly"),
        acceleration_clause=acceleration_clause,
        non_compete_months=get_value(data.founder_terms.non_compete_months, "12"),
        non_solicit_months=get_value(data.founder_terms.non_solicit_months, "24"),
        
        # Transaction Terms
        exclusivity_days=get_value(data.transaction_terms.exclusivity_days, "45"),
        legal_fee_cap=get_value(data.transaction_terms.legal_fee_cap, "$25,000"),
        expected_closing_days=get_value(data.transaction_terms.expected_closing_days, "30"),
        governing_law=get_value(data.transaction_terms.governing_law, "Delaware"),
        
        # Signatures
        binding_status=get_value(data.signatures.binding_status, "non-binding"),
        effective_date_clause=effective_date_clause,
        company_signatory_name=get_value(data.signatures.company_signatory_name, "_________________________"),
        company_signatory_title=get_value(data.signatures.company_signatory_title, "_________________________"),
        investor_signatory_name=get_value(data.signatures.investor_signatory_name, "_________________________"),
        investor_signatory_title=get_value(data.signatures.investor_signatory_title, "_________________________"),
    )
    
    return rendered
