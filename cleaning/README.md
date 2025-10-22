# Cleaning App - Physical Units Structure

This app manages the physical and administrative hierarchy of university cleaning areas.

## 🧭 Entity Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    ENTITY HIERARCHY                         │
└─────────────────────────────────────────────────────────────┘

Physical Hierarchy:          Administrative Hierarchy:
                            
Zone (Campus)                Faculty (Academic Unit)
  ↓ 1-to-Many                  ↓ 1-to-Many
Section (Building)             │
  ↓ 1-to-Many                  │
Unit (Room/Area) ←─────────────┘
```

## 📋 Entity Descriptions

### 1. Zone
**Purpose:** Represents broad areas within the university

**Examples:**
- Main Campus
- Medical Campus  
- Engineering Campus

**Relationships:**
- One Zone → Many Sections (1-to-Many)

**Attributes:**
- `name`: Full name of the zone
- `code`: Short code (e.g., MC, MED, ENG)
- `description`: Brief description

### 2. Section
**Purpose:** Buildings or sub-areas inside a zone

**Examples:**
- Science Building
- Library Block
- Canteen Area

**Relationships:**
- Many Sections → One Zone (Many-to-1)
- One Section → Many Units (1-to-Many)

**Attributes:**
- `zone`: Foreign key to Zone
- `name`: Name of the section
- `code`: Unique section code (e.g., SB-01)
- `floor_count`: Number of floors
- `description`: Brief description

### 3. Faculty
**Purpose:** Administrative divisions of the university

**Examples:**
- Faculty of Science
- Faculty of Arts
- Faculty of Engineering

**Relationships:**
- One Faculty → Many Units (1-to-Many)

**Attributes:**
- `name`: Full faculty name
- `short_name`: Abbreviation (e.g., FOS, FOA)
- `code`: Unique faculty code
- `description`: Faculty description

### 4. Unit (Central Entity)
**Purpose:** Specific areas where cleaning/maintenance is performed

**Examples:**
- Lecture Hall 1
- Lab A
- Office Room 12
- Restroom (3rd Floor)

**Relationships:**
- Many Units → One Section (Many-to-1) [Physical]
- Many Units → One Faculty (Many-to-1) [Administrative]

**Key Features:**
- Connects physical hierarchy (Section → Zone)
- Connects administrative hierarchy (Faculty)
- Has `is_active` status for maintenance tracking

**Attributes:**
- `section`: Foreign key to Section (physical location)
- `faculty`: Foreign key to Faculty (administrative responsibility)
- `name`: Unit name
- `code`: Unique unit code (e.g., SB-01-LH-001)
- `unit_type`: Type (Lecture Hall, Lab, Office, etc.)
- `floor_number`: Floor location
- `area_sqm`: Area in square meters
- `capacity`: People capacity
- `is_active`: Active/Under maintenance status
- `notes`: Special cleaning requirements

## 🔗 Relationship Summary

```
Zone (1) ──────► (Many) Section
                      │
                      │ (1)
                      │
                      ▼
Faculty (1) ────► (Many) Unit
                      ▲
                      │
                      │ (Many)
                      │
                Section (1)
```

## 📊 Data Validation

- Units cannot exceed their section's floor count
- Section names must be unique within a zone
- Unit codes are globally unique
- Faculty protection: Cannot delete a faculty if it has units

## 🎯 Use Cases

1. **Physical Navigation:**
   - Zone → Section → Unit
   - Example: Main Campus → Science Building → Lecture Hall 1 (Floor 3)

2. **Administrative Management:**
   - Faculty → Units
   - Example: Faculty of Science → All labs and lecture halls under FOS

3. **Status Tracking:**
   - Active units available for scheduling
   - Inactive units under maintenance/renovation

## 🔧 Admin Features

- View section/unit counts for each zone
- Filter units by zone, section, faculty, type, and status
- Bulk activate/deactivate units
- Search across all entity fields
- Full location path display for units
