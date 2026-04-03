# Salesforge Contact Fields Reference

## Standard Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `email` | string | **YES** | Primary identifier |
| `first_name` | string | Yes | Used in personalization |
| `last_name` | string | Yes | Used in personalization |
| `company` | string | Recommended | Company name |
| `job_title` | string | Recommended | Contact's role |
| `industry` | string | Optional | Company industry |
| `linkedin_url` | string | Optional | LinkedIn profile URL |
| `phone` | string | Optional | Phone number |
| `website` | string | Optional | Company website |
| `city` | string | Optional | Contact location |
| `state` | string | Optional | State/region |
| `country` | string | Optional | Country |

## Custom Variables

Any additional field becomes a custom variable for personalization:

| Example Variable | Use Case |
|---|---|
| `pain_point` | Personalized pain reference |
| `competitor_tool` | Current tool they use |
| `custom_first_line` | AI-generated opener |
| `tech_stack` | Technologies detected |
| `recent_funding` | Funding amount/round |
| `trigger_signal` | What triggered outreach |

## Field Mapping from Common Sources

### Apollo Export
| Apollo Field | Salesforge Field |
|---|---|
| First Name | first_name |
| Last Name | last_name |
| Email | email |
| Title | job_title |
| Company | company |
| Industry | industry |
| LinkedIn Url | linkedin_url |

### Clay Export
| Clay Field | Salesforge Field |
|---|---|
| First Name | first_name |
| Last Name | last_name |
| Work Email | email |
| Job Title | job_title |
| Company Name | company |
| LinkedIn URL | linkedin_url |
| (any custom column) | (custom variable) |

### LinkedIn Sales Navigator Export
| LinkedIn Field | Salesforge Field |
|---|---|
| First Name | first_name |
| Last Name | last_name |
| Email Address | email |
| Job Title | job_title |
| Company Name | company |
| Profile URL | linkedin_url |
