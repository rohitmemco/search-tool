# PriceNexus - Quick Rebuild Guide
## For Non-Coders Using AI Tools

---

## WHAT YOU'LL BUILD

A price comparison website that:
- Searches for ANY product worldwide
- Shows prices from multiple online stores
- Displays vendor contact information
- Works with multiple currencies
- Has dark mode, filters, charts, and export features

---

## STEP 1: START A NEW PROJECT

Tell the AI:

```
Create a price comparison web app called PriceNexus with:
- React frontend with Tailwind CSS
- Python FastAPI backend
- MongoDB database
- OpenAI GPT integration via Emergent LLM Key

Main feature: User types a product name, gets prices from multiple stores worldwide.
```

---

## STEP 2: BUILD THE SEARCH FEATURE

Tell the AI:

```
Create a search system that:

1. Takes user input like "laptop in India" or "iPhone 15 price USA"

2. Uses AI to understand:
   - What product they want
   - What country/currency to use
   - What stores sell this product

3. Returns 50 results with:
   - Product name and price
   - Store name with link
   - Rating (1-5 stars)
   - Availability (In Stock, Limited, Pre-Order)
   - Vendor contact (name, email, phone, address)

4. Also returns:
   - Price analysis (lowest, highest, average)
   - Market insights text
   - List of stores searched
```

---

## STEP 3: BUILD THE HOMEPAGE

Tell the AI:

```
Create a homepage with:

1. Big search bar in center with:
   - Search icon on left
   - Microphone icon for voice search
   - Submit button on right

2. Example search buttons below:
   "iPhone 15 price in India"
   "Dell Laptop under 50000"
   "Nike shoes"
   "Samsung TV 55 inch"

3. Three feature cards:
   - Universal Search (globe icon)
   - AI-Powered (chart icon)
   - Best Prices (dollar icon)

4. Header with:
   - Heart icon (favorites)
   - Currency dropdown (INR, USD, GBP, EUR, AED)
   - Dark mode toggle (moon/sun)
```

---

## STEP 4: BUILD RESULTS PAGE

Tell the AI:

```
When search completes, show:

1. Price Summary (3 cards):
   - Lowest Price (green)
   - Highest Price (red)
   - Average Price (blue)

2. Controls bar:
   - Filters button
   - Sort dropdown (Price Low/High, Rating, Name)
   - Grid/List view toggle
   - Share button
   - Export Excel button
   - Export PDF button

3. Filter panel with:
   - Price range slider
   - Rating filter (All, 3+, 4+, 4.5+)
   - Availability checkboxes
   - Source type checkboxes

4. Tabs:
   - Products (card grid)
   - Vendors (contact list)
   - Charts (bar + pie)
   - Distribution (area chart)
   - Insights (AI analysis)
   - Sources (store list)
```

---

## STEP 5: BUILD PRODUCT CARDS

Tell the AI:

```
Each product card shows:

1. Product image
2. Product name
3. Price in selected currency
4. Store name badge
5. Star rating
6. Availability status
7. Description snippet
8. Vendor name + "View Details" button
9. Link to store website

Add badges:
- "Lowest Price" (green) on cheapest
- "Best Deal" (orange) on best value

Add buttons:
- Heart icon to save favorite
- Compare icon to add to comparison
```

---

## STEP 6: ADD SPECIAL FEATURES

Tell the AI:

```
Add these features:

1. FAVORITES:
   - Click heart to save
   - Store in browser localStorage
   - View in popup modal

2. COMPARISON:
   - Click compare icon on products
   - Show floating "Compare (X)" button
   - Open modal showing products side-by-side

3. DARK MODE:
   - Toggle with moon icon
   - Save preference in localStorage
   - All colors adapt

4. CURRENCY SWITCH:
   - Dropdown in header
   - Prices convert automatically
   - Support: INR, USD, GBP, EUR, AED

5. VOICE SEARCH:
   - Click microphone
   - Speak your search
   - Auto-fills and searches

6. EXPORTS:
   - PDF: Captures screen, downloads
   - Excel: Creates CSV file
```

---

## STEP 7: VENDOR INFORMATION

Tell the AI:

```
Generate realistic vendor info for each product:

1. Vendor Name (e.g., "Global Traders")
2. Email (clickable)
3. Phone (clickable)
4. Full Address with:
   - Street number and name
   - Area/neighborhood
   - City and state
   - Postal code
   - Country

5. Verification status (Verified Seller, Premium, etc.)
6. Years in business
7. Response time
8. Business hours

Addresses should match the search country:
- India: MG Road, Bangalore, Karnataka - 560066
- USA: 123 Main Street, Suite 456, New York, NY 10001
- UK: Unit 12, High Street, London, EC1A 1BB
- UAE: Office 123, Sheikh Zayed Road, Dubai, P.O. Box 12345
```

---

## STEP 8: AI INTEGRATION

Tell the AI:

```
Use Emergent LLM Key for AI features:

1. PRODUCT DETECTION:
   Query: "cheap gaming laptop"
   AI returns: brands, variations, price range

2. MARKETPLACE DISCOVERY:
   Query: "gaming laptop in India"
   AI returns: Amazon.in, Flipkart, Croma (specific stores)

3. SIMILAR PRODUCTS:
   Query: "iPhone 15"
   AI returns: Samsung Galaxy S24, Google Pixel 8

4. RECOMMENDATIONS:
   Based on search history
   AI suggests related products
```

---

## STEP 9: STYLING

Tell the AI:

```
Apply this design:

FONTS:
- Headings: Manrope (bold)
- Body: DM Sans
- Code: JetBrains Mono

COLORS:
- Primary: Blue #2563eb
- Accent: Purple #7c3aed
- Success: Green #10b981
- Warning: Amber #f59e0b
- Error: Red #ef4444

EFFECTS:
- Cards lift on hover
- Smooth animations
- Gradient buttons (blue to purple)
- Glass-effect header

RESPONSIVE:
- Mobile: 1 column
- Tablet: 2 columns
- Desktop: 3-4 columns
```

---

## STEP 10: FINAL CONFIGURATION

Set these environment variables:

**Backend (.env):**
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=pricenexus_db
CORS_ORIGINS=*
EMERGENT_LLM_KEY=your-key-here
```

**Frontend (.env):**
```
REACT_APP_BACKEND_URL=https://your-backend-url
```

---

## TESTING CHECKLIST

After building, verify:

- [ ] Search works with different products
- [ ] Prices show in selected currency
- [ ] Dark mode toggles correctly
- [ ] Filters narrow down results
- [ ] Sorting changes order
- [ ] Favorites save and persist
- [ ] Compare shows side-by-side
- [ ] Voice search recognizes speech
- [ ] PDF downloads successfully
- [ ] Excel/CSV downloads
- [ ] Vendor details are realistic
- [ ] All 6 tabs show data
- [ ] External links work

---

## COMMON ISSUES

| Problem | Solution |
|---------|----------|
| Search takes forever | Normal - AI needs 5-10 seconds |
| No results | Try simpler search terms |
| Wrong currency | Check currency dropdown |
| Voice not working | Use Chrome browser |
| PDF export fails | Refresh and retry |

---

## NEED MORE DETAILS?

See the full documentation:
`/app/docs/COMPLETE_DOCUMENTATION.md`

This has:
- Complete API specifications
- All component breakdowns
- Database schemas
- Error handling
- Troubleshooting guide

---

*Built with Emergent AI Platform*
