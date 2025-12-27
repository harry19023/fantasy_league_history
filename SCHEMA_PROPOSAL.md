# Database Schema Proposal

## Overview
The schema is organized around **League** as the root object. Everything belongs to a league.

## Core Entities

### 1. League
- Root entity - everything belongs to a league
- **Fields:**
  - `id` (PK)
  - `name` (String)
  - `settings` (JSON) - league configuration

### 2. Franchise
- Represents the same team year over year
- Belongs to a league
- Leagues should have the same franchises unless teams grow/shrink
- **Fields:**
  - `id` (PK)
  - `league_id` (FK → League)
  - `name` (String) - franchise name (e.g., "The Warriors")

### 3. Manager
- Human owners of franchises
- A franchise can change managers over time (different managers in different seasons)
- **Fields:**
  - `id` (PK)
  - `name` (String) - manager name

### 4. Season
- Each year is a new season
- Belongs to a league
- **Fields:**
  - `id` (PK)
  - `league_id` (FK → League)
  - `year` (Integer) - e.g., 2024
  - `start_date` (Date, nullable)
  - `end_date` (Date, nullable)

### 5. FranchiseSeason
- Franchise stats for a specific season
- Links franchise to season with season-specific stats
- Managers own a franchise for an entire season
- **Fields:**
  - `id` (PK)
  - `franchise_id` (FK → Franchise)
  - `season_id` (FK → Season)
  - `manager_id` (FK → Manager) - manager who owned this franchise this season
  - `regular_wins` (Integer, default=0) - regular season wins
  - `regular_losses` (Integer, default=0) - regular season losses
  - `playoff_winners_wins` (Integer, default=0) - wins in winners bracket
  - `playoff_winners_losses` (Integer, default=0) - losses in winners bracket
  - `playoff_losers_wins` (Integer, default=0) - wins in losers bracket
  - `playoff_losers_losses` (Integer, default=0) - losses in losers bracket
  - `points_for` (Float, default=0.0) - total points scored (regular + playoffs)
  - `points_against` (Float, default=0.0) - total points against (regular + playoffs)
  - `final_standing` (Integer, nullable) - final ranking (1st, 2nd, 3rd, etc.)
  - `prize_money` (Float, default=0.0) - money prize amount
  - `won_championship` (Boolean, default=False) - won championship (1st place)
  - `won_draft_lottery` (Boolean, default=False) - won losers bracket
  - `lost_beer_mile` (Boolean, default=False) - lost losers bracket (last place)
  - Unique constraint: (franchise_id, season_id)

### 6. Game
- Games between franchises in a season (regular season or playoffs)
- **Fields:**
  - `id` (PK)
  - `season_id` (FK → Season)
  - `week` (Integer) - week number in season (or playoff round)
  - `game_type` (String) - "REGULAR", "PLAYOFF_WINNERS", "PLAYOFF_LOSERS"
  - `franchise1_id` (FK → Franchise)
  - `franchise2_id` (FK → Franchise)
  - `franchise1_score` (Float, nullable)
  - `franchise2_score` (Float, nullable)
  - `game_date` (Date, nullable)

### 7. Player
- Players are not tied to franchises (they can be on different teams)
- **Fields:**
  - `id` (PK)
  - `name` (String)
  - `position` (String) - e.g., "QB", "RB", "WR", etc.
  - `nfl_team` (String, nullable) - NFL team they play for

### 8. Lineup
- Represents a player in a specific game's lineup (roster for that week)
- Includes both starters and bench players
- Links player to game with their score for that week
- **Note**: If a player is in a lineup, they must have been on that franchise's roster at that time
- Roster membership can be inferred from lineup entries (which franchises/seasons a player appeared in)
- **Fields:**
  - `id` (PK)
  - `game_id` (FK → Game)
  - `franchise_id` (FK → Franchise) - which franchise's lineup
  - `player_id` (FK → Player)
  - `score` (Float, nullable) - player's score for this game
  - `position` (String, nullable) - position in this lineup (e.g., "QB", "RB", "WR", "TE", "K", "DEF", "BENCH")
  - Unique constraint: (game_id, franchise_id, player_id)

## Relationships Summary

```
League
  ├── Franchise (1:N)
  │     ├── FranchiseSeason (1:N) → Season (N:1) → Manager (N:1)
  │     └── Game (N:1 via franchise1_id/franchise2_id)
  │           └── Lineup (1:N)
  │                 └── Player (N:1)
  └── Season (1:N)
        ├── FranchiseSeason (1:N) → Manager (N:1)
        └── Game (1:N)
              └── Lineup (1:N)
```

## Key Design Decisions

1. **Franchise vs Team**: Franchise is persistent across seasons, while the old "Team" concept was season-specific. Franchise represents continuity.

2. **Manager Tracking**: Managers are linked directly to FranchiseSeason, meaning each franchise has one manager per season. Manager changes are tracked by comparing managers across different seasons for the same franchise.

3. **Season Stats**: FranchiseSeason stores aggregated stats (wins, losses, points) that can be calculated from games but stored for performance. Stats are separated by game type:
   - Regular season wins/losses
   - Winners bracket playoff wins/losses
   - Losers bracket playoff wins/losses
   - Final standings and prizes (championship, draft lottery, beer mile)

4. **Lineup**: Each lineup entry represents a player's participation in a specific game, with their score for that week. This allows tracking which players were in which lineups and their performance.

5. **Roster Membership Inference**: Roster membership can be inferred from Lineup entries:
   - If a player appears in a lineup for a franchise, they were on that franchise's roster at that time
   - This includes both starters (position like "QB", "RB", etc.) and bench players (position="BENCH")
   - We can determine which franchises a player has been on by looking at distinct franchise_id values in Lineup
   - We can determine which seasons by joining Lineup → Game → Season
   - **Note**: This tracks all players who were on the roster for a given week, whether they started or were on the bench

6. **Player Independence**: Players are not tied to franchises - they're independent entities that can appear in different lineups across different games/seasons.

7. **Player History Queries**: With Lineup and Game tables, we can answer:
   - Which franchises has a player been on? (distinct franchise_id from Lineup)
   - When were they on each franchise? (from Lineup → Game → Season)
   - How many games did they win for each franchise? (from Lineup + Game, where their team won)
   - How many points did they score for each franchise? (sum of Lineup.score grouped by franchise)

## Migration Notes

- Old `Team` model → New `Franchise` model
- Old `Matchup` model → New `Game` model
- Old `Roster` model → New `Lineup` model (roster membership inferred from lineup entries)
- New models: `Manager`, `Season`, `FranchiseSeason`
- `League.year` field should be removed (year is now in Season)

## Playoff Structure

### Winners Bracket
- Top teams compete for championship
- Winner gets: 1st place prize money + Championship
- 2nd place gets: 2nd place prize money
- 3rd place gets: 3rd place prize money

### Losers Bracket
- Bottom teams compete in consolation bracket
- Winner gets: Draft Lottery
- Loser gets: Beer Mile

### Tracking
- `Game.game_type` distinguishes regular season from playoff games
- `Game.game_type` = "PLAYOFF_WINNERS" or "PLAYOFF_LOSERS" for playoff games
- `FranchiseSeason` tracks wins/losses separately for each bracket
- `FranchiseSeason` tracks final standings and prizes

## Query Examples

### Player History by Franchise
```sql
-- Which franchises has a player been on? (and which seasons)
SELECT DISTINCT f.name, s.year
FROM lineups l
JOIN games g ON l.game_id = g.id
JOIN franchises f ON l.franchise_id = f.id
JOIN seasons s ON g.season_id = s.id
WHERE l.player_id = ?
ORDER BY s.year, f.name

-- How many games did a player win for each franchise? (regular season only)
SELECT f.name, COUNT(*) as regular_season_wins
FROM lineups l
JOIN games g ON l.game_id = g.id
JOIN franchises f ON l.franchise_id = f.id
WHERE l.player_id = ?
  AND g.game_type = 'REGULAR'
  AND (
    (l.franchise_id = g.franchise1_id AND g.franchise1_score > g.franchise2_score)
    OR
    (l.franchise_id = g.franchise2_id AND g.franchise2_score > g.franchise1_score)
  )
GROUP BY f.id, f.name

-- Playoff wins by bracket
SELECT
  f.name,
  COUNT(CASE WHEN g.game_type = 'PLAYOFF_WINNERS' AND
    ((l.franchise_id = g.franchise1_id AND g.franchise1_score > g.franchise2_score)
     OR (l.franchise_id = g.franchise2_id AND g.franchise2_score > g.franchise1_score))
    THEN 1 END) as winners_bracket_wins,
  COUNT(CASE WHEN g.game_type = 'PLAYOFF_LOSERS' AND
    ((l.franchise_id = g.franchise1_id AND g.franchise1_score > g.franchise2_score)
     OR (l.franchise_id = g.franchise2_id AND g.franchise2_score > g.franchise1_score))
    THEN 1 END) as losers_bracket_wins
FROM lineups l
JOIN games g ON l.game_id = g.id
JOIN franchises f ON l.franchise_id = f.id
WHERE l.player_id = ?
GROUP BY f.id, f.name

-- Total points scored by player per franchise
SELECT f.name, SUM(l.score) as total_points, COUNT(l.id) as games_played
FROM lineups l
JOIN franchises f ON l.franchise_id = f.id
WHERE l.player_id = ?
GROUP BY f.id, f.name
ORDER BY total_points DESC

-- Player stats per franchise per season
SELECT
  f.name as franchise,
  s.year as season,
  COUNT(l.id) as weeks_on_roster,
  COUNT(CASE WHEN l.position != 'BENCH' THEN 1 END) as games_started,
  COUNT(CASE WHEN l.position = 'BENCH' THEN 1 END) as weeks_on_bench,
  SUM(l.score) as total_points,
  AVG(l.score) as avg_points,
  COUNT(CASE
    WHEN g.game_type = 'REGULAR' AND
      ((l.franchise_id = g.franchise1_id AND g.franchise1_score > g.franchise2_score)
       OR (l.franchise_id = g.franchise2_id AND g.franchise2_score > g.franchise1_score))
    THEN 1
  END) as regular_season_wins,
  COUNT(CASE
    WHEN g.game_type IN ('PLAYOFF_WINNERS', 'PLAYOFF_LOSERS') AND
      ((l.franchise_id = g.franchise1_id AND g.franchise1_score > g.franchise2_score)
       OR (l.franchise_id = g.franchise2_id AND g.franchise2_score > g.franchise1_score))
    THEN 1
  END) as playoff_wins
FROM lineups l
JOIN games g ON l.game_id = g.id
JOIN franchises f ON l.franchise_id = f.id
JOIN seasons s ON g.season_id = s.id
WHERE l.player_id = ?
GROUP BY f.id, f.name, s.id, s.year
ORDER BY s.year DESC, total_points DESC

-- Franchise season standings and prizes
SELECT
  f.name as franchise,
  s.year as season,
  fs.regular_wins,
  fs.regular_losses,
  fs.playoff_winners_wins,
  fs.playoff_winners_losses,
  fs.playoff_losers_wins,
  fs.playoff_losers_losses,
  fs.final_standing,
  fs.prize_money,
  CASE WHEN fs.won_championship THEN 'Yes' ELSE 'No' END as championship,
  CASE WHEN fs.won_draft_lottery THEN 'Yes' ELSE 'No' END as draft_lottery,
  CASE WHEN fs.lost_beer_mile THEN 'Yes' ELSE 'No' END as beer_mile
FROM franchise_seasons fs
JOIN franchises f ON fs.franchise_id = f.id
JOIN seasons s ON fs.season_id = s.id
WHERE s.year = ?
ORDER BY fs.final_standing

-- Only count games where player started (not bench)
SELECT f.name, COUNT(*) as wins_as_starter
FROM lineups l
JOIN games g ON l.game_id = g.id
JOIN franchises f ON l.franchise_id = f.id
WHERE l.player_id = ?
  AND l.position != 'BENCH'
  AND (
    (l.franchise_id = g.franchise1_id AND g.franchise1_score > g.franchise2_score)
    OR
    (l.franchise_id = g.franchise2_id AND g.franchise2_score > g.franchise1_score)
  )
GROUP BY f.id, f.name
```
