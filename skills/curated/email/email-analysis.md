# Email Analysis Patterns

## Header Parsing
- From/To/CC/BCC: extract name and email address parts
- Date: parse various formats (RFC 2822, ISO 8601)
- Message-ID and In-Reply-To: for thread reconstruction

## Thread Reconstruction
- Build parent-child relationships from In-Reply-To headers
- Group by subject line (strip Re: Fwd: prefixes)
- Sort within threads by date

## Content Analysis
- Extract action items: look for keywords (ACTION, TODO, please, could you)
- Identify decisions: DECISION, agreed, approved, decided
- Signature detection: delimiter line (--) followed by contact info

## Classification
- Keyword-based: map keyword sets to categories
- Priority: urgent/important keywords, sender VIP lists
- Sentiment: positive/negative word frequency analysis
