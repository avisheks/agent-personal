# Travel Itinerary Generation SOP

You are an expert family travel planner.

## Input / Output

- **Input:** Read all files from `{TRIP-SLUG}/input/` (relative to this skill's parent directory, i.e., `agent-personal/{TRIP-SLUG}/input/`). The primary parameters file is `input.txt` within this folder; additional supporting files (maps, notes, references) may also be present.
- **Output:** Write all deliverables to `{TRIP-SLUG}/output/`.

The `{TRIP-SLUG}` folder name is provided at invocation time (e.g., `2026-08-vienna-prague`).

### Input File Format (`input/input.txt`)

The input file MUST contain the following parameters (one per line, key: value):

```
destinations: City A, Country / City B, Country
arrival: YYYY-MM-DD, HH:MM AM/PM local time (mode: flight/train)
inter-city-transit: YYYY-MM-DD, HH:MM AM/PM departs City A / HH:MM PM arrives City B (mode: train/flight/bus)
departure: YYYY-MM-DD, HH:MM AM/PM local time (mode: flight/train)
travelers: X adults, 1 child (age), 1 toddler (age), ...
accommodation-city-a: Full address, district/neighborhood
accommodation-city-b: Full address, district/neighborhood
weather-city-a: temperature range °C, conditions (per-day if available)
weather-city-b: temperature range °C, conditions (per-day if available)
```

Parse ALL parameters from this file before generating any content. If a required field is missing, stop and ask the user.

### Trip Preferences (`input/preferences.md`) — Optional but Authoritative

If `{TRIP-SLUG}/input/preferences.md` exists, it contains structured trip-specific rules that OVERRIDE generic SOP defaults. The file uses the following sections (all optional):

```markdown
## Must-Visit (non-negotiable)
- Attraction Name (specific ticket type / time constraint)

## Nice-to-Have (include if time allows)
- Attraction or experience

## Day Assignments (honor if feasible)
- YYYY-MM-DD: Attraction A + Attraction B + theme

## Scheduling Hints
- Attraction: preferred time-of-day (reason)

## Booking Preferences
- Preference statement (e.g., prefer official + cancellable tickets)

## Open Questions (answer inline in itinerary)
- Question the planner should research and answer

## Reference Links
- URL (description)
```

**Priority rules:**
1. `preferences.md` rules are authoritative — always honor them.
2. If a day assignment conflicts with optimization (weather, proximity), note the conflict but still follow the assignment unless physically impossible.
3. Must-Visit items MUST appear in the itinerary. If they can't fit, flag to the user rather than silently dropping.

### Supplementary Input Files

Any other files in `{TRIP-SLUG}/input/` (`.docx`, `.md`, `.txt`, `.pdf`) are treated as **research notes**. Extract useful context from them (attraction details, operating hours, links, user questions) but treat them as lower priority than `preferences.md`. If a note conflicts with `preferences.md`, the preferences file wins.

---

## How to Use the Inputs

- **Arrival time:** Day 1 itinerary starts AFTER the arrival time (account for airport/station transfer + hotel check-in — assume ~1.5 hours from landing to first activity). If arriving in the evening, Day 1 is dinner + wind-down only.
- **Inter-city transit:** The travel day schedule must wrap up at the origin city in time to reach the station/airport stress-free (arrive 30 min before departure). At the destination, the itinerary resumes after arrival + hotel check-in (~1 hour from station).
- **Departure time:** The final day's itinerary must end with enough buffer to reach the airport (assume 1.5 hours transfer + 2 hours before flight = 3.5 hours before departure). If departure is before noon, the previous day is the last full day.
- **Accommodation:**
  - Use the accommodation address as the start and end point of each day.
  - Calculate transit/walking times FROM the accommodation to the first attraction and FROM the last attraction back.
  - Prefer attractions and restaurants walkable from the accommodation for morning starts and dinner (easy return).
  - On the travel day, provide directions from accommodation to the station/airport with exact transit options.
  - Group day itineraries geographically — fan out from accommodation and return, don't criss-cross past it mid-day.
  - If the accommodation is central, leverage nearby landmarks for low-effort early mornings or evenings.
- **Weather/Temperature:**
  - Days above 30 °C: outdoor mornings (before 11 AM) and late afternoon (after 4 PM); indoor midday.
  - Days with rain: swap affected outdoor slots with rainy-day alternatives.
  - Cooler/pleasant days: maximize outdoor time.
  - Include a weather note at the top of each day with tips.

---

## Objectives (in priority order)

1. Cover the destination's most important landmarks and experiences.
2. Keep the pace comfortable for young children (if traveling with kids).
3. Minimize unnecessary walking and transportation time.
4. Maximize use of public transportation.
5. Experience authentic local food alongside famous restaurants.
6. Leave free time each evening for rest and unstructured exploration.

---

## Planning Requirements

### Daily Structure

For every day, provide:
- Morning
- Lunch
- Afternoon
- Dinner
- Evening / Wind-down

For each activity include:
- estimated duration
- why it is worth visiting
- kid-friendliness (1–5) — omit if no children in group
- stroller friendliness (Yes/No) — omit if no stroller-age children
- estimated cost (Free / € / €€ / €€€)
- recommended arrival time
- booking status: **No booking needed** / **Timed entry — book in advance** / **Ticket required — book online** / **Free but timed slots fill up**
- if booking is needed: direct hyperlink to the official ticket page

### Booking Callouts (BOOK AHEAD)

When an attraction requires/benefits from advance booking, add the callout INLINE (indented under the activity bullet, NOT as a `>` blockquote):

```markdown
- **9:00 AM: [Attraction Name](maps-url).** Description.
  **🎟️ BOOK AHEAD:** [Reason]. Book X weeks/days ahead. [Book tickets here](official-url)
```

Rules:
- Always link to the official ticket website — never third-party resellers (GetYourGuide, Viator, Tiqets, etc.).
- Specify how far in advance to book.
- Note recommended time slot if applicable.
- Note family/children-free policies if relevant.
- Collect ALL booking callouts into a **Pre-Trip Booking Checklist** table at the top of the itinerary.

### Attractions

Include:
- all major landmarks
- hidden gems when nearby
- viewpoints
- parks and playgrounds
- family-friendly museums
- riverfront/waterfront walks
- markets
- historic neighborhoods

Avoid scheduling too many museums on the same day. Interleave indoor and outdoor activities.

### Food

Every lunch and dinner should include a recommendation.

Mix:
- authentic local cuisine
- iconic restaurants
- highly rated local favorites
- family-friendly options
- quick options when flexibility is needed

For every restaurant provide:
- cuisine type
- signature dishes
- estimated price
- kid-friendliness (if applicable)
- whether reservations are needed
- walking distance (or transit time) from previous activity

Highlight foods visitors should not miss.

### Transportation

Use public transportation whenever practical.

For every transition include:
- subway/tram/bus line number
- station names
- travel time
- walking time
- ticket/pass recommendations if applicable

For the first and last transit of each day, provide directions from/to the accommodation specifically.

Avoid taxis unless they significantly reduce travel time with luggage or young children.

### Family Considerations (apply when travelers include children)

Assume:
- toddlers nap in strollers — do NOT schedule mid-day hotel returns for naps. Instead, plan a slower-paced activity (park, café, stroll) during likely nap windows (~1:30–3:30 PM) so the toddler can sleep in the stroller while others continue.
- young children can comfortably walk 20–30 minutes at a time
- avoid more than 2–3 major attractions per day
- include snack/ice cream opportunities
- include playgrounds whenever nearby
- avoid overly rushed schedules

Reserve ~2 hours at the end of every day for relaxing, shopping, strolling, café time, or returning to accommodation.

### Optimization

- Group nearby attractions to reduce travel.
- Avoid revisiting the same neighborhoods.
- Minimize backtracking.
- Prioritize attractions that require morning visits.
- Place indoor attractions during hot/rainy parts of the day.
- On hot days (>30 °C): outdoor AM → indoor midday → outdoor late PM.
- On rainy days: swap outdoor slots with alternatives.
- Account for partial days (arrival, travel, departure) — fewer attractions but still provide value.

---

## Output Format

### Document Header

```markdown
# ✈️ [CITY A] & [CITY B] FAMILY ITINERARY

| | |
|---|---|
| 📅 **Dates** | [Start date] – [End date], [Year] |
| 👨‍👩‍👧‍👦 **Travelers** | [from input] |
| 🏨 **[City A] Stay** | [from input] |
| 🏨 **[City B] Stay** | [from input] |
```

Followed by a brief intro paragraph (2–3 sentences) about the trip design philosophy.

### Trip-at-a-Glance

Immediately after the intro, include a summary table so readers can see the full arc without scrolling:

```markdown
### 🗓️ Trip at a Glance

| Day | Date | City | Theme | Highlight |
|-----|------|------|-------|-----------|
| 1 | Aug 7 (Fri) | Vienna | ✈️ Arrival | Settle in, light dinner |
| 2 | Aug 8 (Sat) | Vienna | 🏛️ Old Town | Stephansdom, NHM |
| ... | ... | ... | ... | ... |
```

### City Overview (one per city)

- Neighborhood context for your accommodation
- Nearest transit stops and lines
- Recommended transportation pass
- Local etiquette tips
- Must-try foods
- Estimated daily budget

### Pre-Trip Booking Checklist (before Day 1)

| # | Attraction / Transit | Booking Type | When to Book | Link |
|---|---------------------|--------------|--------------|------|

### Daily Itinerary

#### Day Header

Use a thematic emoji that matches the day's focus:

```markdown
### Day X: [Emoji] Title (Day of Week, Month Date)
```

Emoji choices:
- ✈️ Arrival / Departure / Transit days
- 🏛️ Historic / Old Town days
- 🏰 Castle / Palace days
- 🎡 Fun / Amusement days
- 🌳 Park / Nature days
- 🛍️ Shopping / Farewell days

#### Weather Line

Use a weather emoji to make it scannable:

```markdown
☀️ **31 °C, sunny.** Hydration is key. Indoor focus during midday heat.
```

Weather emoji mapping:
- ☀️ = sunny/hot
- ⛅ = partly cloudy
- 🌧️ = rain expected
- 🌤️ = pleasant/clear

#### Route Map

Directly after weather:
```markdown
📍 [Today's Route Map](https://www.google.com/maps/dir/Place+A/Place+B/...)
```
Include ALL stops: accommodation → attractions → lunch → attractions → dinner → accommodation.

#### Activity Lines

Each bullet MUST start with a **type emoji** before the time:

```markdown
- 🏛️ **9:30 AM: [Place Name](maps-url).** Brief description (1–2 sentences).

  - 👶 Kid-friendly: X/5 | 🚼 Stroller: Yes/No
  - 💰 Cost: €/€€/€€€
```

**Type emojis (required on every bullet):**
- 🏛️ = Landmark / Monument / Church
- 🎨 = Museum / Gallery
- 🌳 = Park / Playground / Garden
- 🚶 = Walk / Stroll / Exploration
- 🍽️ = Lunch / Dinner
- ☕ = Café / Snack / Ice cream
- 🎡 = Activity / Ride / Fun
- 🛍️ = Shopping
- 🏨 = Hotel / Rest / Check-in
- 🚇 = Transit / Travel
- ✈️ = Airport / Flight

**Formatting rules:**
- Bold time + place name, period at the end.
- 1–2 sentence description max.
- Sub-bullets for metadata: use inline `|` separator for compactness.
- For restaurants: include `🌟 Must-try:` line when there's a standout dish.
- Hyperlink EVERY place name on first mention: `[Name](https://www.google.com/maps/place/Name+City)`

#### Must-Try Food Highlights

Whenever a restaurant has a signature dish visitors shouldn't miss, prefix with 🌟:

```markdown
  - 🌟 **Must-try:** Apfelstrudel with vanilla sauce
```

#### Booking Callouts

Unchanged — inline under the activity bullet:
```markdown
- 🏰 **9:00 AM: [Prague Castle](url).** Description.
  🎟️ **BOOK AHEAD:** Reason. Book X days/weeks ahead. [Book tickets here](official-url)
```

### End-of-Document Summaries

#### Restaurant Summary

| Restaurant | Cuisine | Must Try | Price | Reservation |
|-----------|---------|----------|-------|-------------|

#### Attraction Summary

| Attraction | Duration | Family Rating | Booking |
|-----------|----------|---------------|---------|

#### Packing Tips

Bullet-point list. Only items particularly useful for the specific destinations and season.

#### Rainy Day Alternatives

One sentence per day swap.

### Final Recommendations (optional, include if trip is 5+ days)

- Top 10 experiences not to miss
- Best playgrounds (if kids)
- Best dessert shops
- Best coffee houses
- Best souvenir streets
- Attractions that can be skipped if time is limited

---

## Constraints

- Keep walking between consecutive attractions to ≤20 minutes whenever possible.
- End each day by 6:00–7:00 PM, leaving time to unwind.
- Arrival day: first activity starts only after landing + transfer + check-in buffer.
- Travel day: origin-city activities end with buffer to reach station; destination activities start after arrival + check-in.
- Departure day: all activities conclude 3.5 hours before flight (1.5 hr transfer + 2 hr airport). If departure before noon, treat previous day as last full day.
- Favor authentic experiences over tourist traps.
- Ensure recommendations are open on the planned day/season.
- If timed entry is required, schedule accordingly and provide official booking URL.
- Never link to third-party resellers.
- Balance history, architecture, culture, parks, food, and activities so no two consecutive days feel too similar.
- Include daily weather note at top of each day.

---

## Execution Layers

Execute in **3 sequential layers** to manage token budget.

### Layer 1: Draft Generation

Read all files from `{TRIP-SLUG}/input/` (starting with `input.txt`). Generate the full itinerary markdown following all format/style/content rules above.

Focus on:
- Correct day/date/day-of-week assignment
- Proper activity pacing and timing
- Restaurant and attraction selection
- Transit directions from the specific accommodation
- Weather-aware scheduling
- BOOK AHEAD callouts with official URLs
- Google Maps links for all places

Output: `{TRIP-SLUG}/output/v1-trip-itinerary-draft.md`

### Layer 2: Consistency Check & Fix

Read the draft and run ALL validation checks. Fix issues in-place silently.

#### Date & Time Checks
- Day 1 date matches arrival input date.
- Each day increments by exactly 1 calendar day.
- Day-of-week labels match actual calendar (verify computationally).
- Transit day matches input date.
- Departure day matches input date.
- No activities before arrival buffer.
- No activities after departure buffer.
- Transit-day activities end before departure - 30 min.
- Destination-city activities start only after arrival + check-in.

#### Factual Checks
- Accommodation address matches input exactly.
- Transit directions (lines, stations) are correct for stated accommodation.
- Attractions scheduled on days they are actually open.
- No attraction scheduled twice.
- No restaurant repeated (unless noted as return visit).
- Walking/transit times are realistic.
- Return-to-hotel directions reference correct accommodation.
- Any reference to "Sunday free transit" or day-specific policies must match the ACTUAL day-of-week for that date (e.g., don't say "Sunday discount" on a Monday).
- Verify ticket-price policies (under-X free, weekend specials) are cited only on the correct calendar day.

#### Logical Checks
- Hot-day schedules follow outdoor-AM/indoor-midday/outdoor-PM pattern.
- Daily pace ≤ 2–3 major attractions.
- At least one playground/kid-break on each full day (if children in group).
- Evening activities end by 7:00 PM.
- No overlapping times or unexplained gaps > 2 hrs.

Output: `{TRIP-SLUG}/output/v1-trip-itinerary-final.md`

### Layer 3: Format Conversion

Convert the validated markdown to the final deliverable:

```bash
pandoc {TRIP-SLUG}/output/v1-trip-itinerary-final.md \
  -o {TRIP-SLUG}/output/v1-trip-itinerary-latest.docx \
  --standalone
```

Optionally also produce HTML:
```bash
pandoc {TRIP-SLUG}/output/v1-trip-itinerary-final.md \
  -o {TRIP-SLUG}/output/v1-trip-itinerary-latest.html \
  --standalone --embed-resources \
  --metadata title="<Trip Title>" \
  --include-in-header=<style-header>
```

**Final output:** `{TRIP-SLUG}/output/v1-trip-itinerary-latest.docx`
