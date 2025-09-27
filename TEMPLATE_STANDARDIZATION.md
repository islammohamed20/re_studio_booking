# Template Standardization Project

## Overview

This project aims to standardize all templates in the Re Studio Booking application by converting them to a unified format that:

1. Uses Frappe's template inheritance system properly
2. Includes a consistent sidebar navigation component
3. Implements consistent styling with standardized color variables
4. Uses English language by default for all interface elements
5. Follows proper layout and responsive design principles

## Implemented Changes

The following changes have been implemented:

### Core Template Structure

All pages now follow this template structure:

```jinja
{% extends "templates/web.html" %}

{% block title %}Page Title - {{ title }}{% endblock %}

{% block head_include %}
<!-- Standardized styles and meta tags -->
{% endblock %}

{% block content %}
<div class="flex h-screen" style="direction: ltr;">
    <!-- Unified Sidebar -->
    {% include "re_studio_booking/www/components/sidebar.html" %}
    
    <!-- Main Content -->
    <div class="flex-1 flex flex-col overflow-hidden main-content">
        <!-- Header -->
        <header>...</header>
        
        <!-- Content -->
        <main>...</main>
    </div>
</div>
{% endblock %}
```

### Standardized Sidebar

A unified sidebar component has been created and is included in all pages using:

```jinja
{% include "re_studio_booking/www/components/sidebar.html" %}
```

The sidebar provides consistent navigation across the application.

### Standardized Color Variables

CSS variables have been defined for consistent color usage:

```css
:root {
    --primary-color: #ff0000;
    --secondary-color: #1e1e1e;
    --tertiary-color: #f2f2f2;
    --white: #ffffff;
    --surface-selected: rgba(255, 0, 0, 0.1);
    --ink-gray-5: #666666;
    --ink-gray-9: #000000;
    --outline-gray-3: #cccccc;
}
```

### English Language UI

All UI text has been standardized to English to ensure consistency across the application.

### Responsive Design

All pages use a combination of Flexbox and Grid layouts to ensure proper responsiveness across different screen sizes.

## Pages Standardized

The following pages have been standardized:

- Admin Dashboard (`admin-dashboard.html`)
- Bookings (`bookings.html`)
- Booking Form (`booking-form.html`)
- Categories (`categories.html`)
- Services (`services.html`)
- Photographers (`photographers.html`)
- Settings (`settings.html`)
- Packages (`packages.html`)

## How to Apply Changes

To apply these standardized templates to your installation:

1. Run the provided shell script to standardize all templates:

```bash
cd /path/to/frappe/apps/re_studio_booking/re_studio_booking/www
chmod +x standardize_templates.sh
./standardize_templates.sh
```

Or alternatively, run the Python script directly:

```bash
cd /path/to/frappe/apps/re_studio_booking
chmod +x standardize_templates.py
./standardize_templates.py
```

2. Restart the Frappe server to apply the changes:

```bash
bench restart
```

## Customization

The templates are designed to be easily customizable:

- To change colors: Edit the CSS variables in each template's `head_include` block
- To modify the sidebar: Edit the `components/sidebar.html` file
- To adjust layouts: Each page has clearly defined sections in the main content area

## Future Improvements

Future improvements could include:

1. Moving shared CSS to a separate CSS file that can be included in all templates
2. Adding more customization options through settings
3. Implementing RTL (right-to-left) support for Arabic language
4. Adding theme switching capabilities

## Support

For any questions or issues related to these template changes, please contact the development team.
