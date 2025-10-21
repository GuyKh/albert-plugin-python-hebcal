# -*- coding: utf-8 -*-

"""Convert Hebrew dates to Gregorian and vice versa using Hebcal API.

Supports various date input formats:
- Hebrew to Gregorian: "5784 Kislev 25", "25 Kislev 5784", "Kislev 25, 5784"
- Gregorian to Hebrew: "2023-12-08", "12/8/2023", "December 8, 2023"

Synopsis: <trigger> [date]"""

from albert import *
import json
import urllib.request
import urllib.parse
import re
from pathlib import Path
import sys

# Metadata for Albert v4.0
md_iid = "4.0"
md_version = "0.0.1"
md_name = "Hebrew Calendar Converter"
md_description = "Convert Hebrew dates to Gregorian and vice versa"
md_url = "https://github.com/albertlauncher/albert-plugin-python-hebcal"
md_authors = ["@GuyKh"]
md_maintainers = ["@GuyKh"]

iconPath = str(Path(__file__).parent / "logo.svg")

# Hebrew month names mapping
HEBREW_MONTHS = {
    'tishrei': 'Tishrei', 'cheshvan': 'Cheshvan', 'kislev': 'Kislev',
    'tevet': 'Tevet', 'shvat': 'Shvat', 'adar': 'Adar', 'adar1': 'Adar1',
    'adar2': 'Adar2', 'nisan': 'Nisan', 'iyyar': 'Iyyar', 'sivan': 'Sivan',
    'tamuz': 'Tamuz', 'av': 'Av', 'elul': 'Elul'
}


class Plugin(PluginInstance, TriggerQueryHandler):
    def __init__(self):
        PluginInstance.__init__(self)
        TriggerQueryHandler.__init__(self)

    def id(self):
        return md_name

    def name(self):
        return md_name

    def description(self):
        return md_description

    def defaultTrigger(self):
        return "hebcal "

    def handleTriggerQuery(self, query):
        query_string = query.string.strip()
        
        # Debug logging
        debug(f"[hebcal] Query triggered with: '{query_string}'")
        
        if not query_string:
            query.add(StandardItem(
                id=md_name,
                icon_factory=lambda: makeImageIcon(iconPath),
                text="Hebrew Calendar Converter",
                subtext="Enter a Hebrew or Gregorian date to convert"
            ))
            return

        items = []

        # Try to parse as Gregorian date
        gregorian_result = parseGregorianDate(query_string)
        debug(f"[hebcal] Gregorian parse result: {gregorian_result}")
        if gregorian_result:
            hebrew_date = convertGregorianToHebrew(gregorian_result)
            debug(f"[hebcal] Hebrew conversion: {hebrew_date}")
            if hebrew_date:
                items.append(createResultItem(gregorian_result, hebrew_date, False))

        # Try to parse as Hebrew date
        hebrew_result = parseHebrewDate(query_string)
        debug(f"[hebcal] Hebrew parse result: {hebrew_result}")
        if hebrew_result:
            gregorian_date = convertHebrewToGregorian(hebrew_result)
            debug(f"[hebcal] Gregorian conversion: {gregorian_date}")
            if gregorian_date:
                items.append(createResultItem(hebrew_result, gregorian_date, True))

        debug(f"[hebcal] Adding {len(items)} items")

        if not items:
            query.add(StandardItem(
                id=md_name,
                icon_factory=lambda: makeImageIcon(iconPath),
                text="Invalid date format",
                subtext="Try formats like '5784 Kislev 25', '2023-12-08', or 'December 8, 2023'"
            ))
        else:
            for item in items:
                query.add(item)

def parseHebrewDate(date_str):
    """Parse Hebrew date string into components."""
    # Remove common punctuation
    cleaned = re.sub(r'[,.]', '', date_str).lower()
    parts = cleaned.split()
    
    if len(parts) < 3:
        return None
    
    year, month, day = None, None, None
    
    # Try different arrangements
    for part in parts:
        if part.isdigit():
            num = int(part)
            if num > 5000:  # Hebrew year
                year = num
            elif 1 <= num <= 30:  # Day
                day = num
        elif part in HEBREW_MONTHS:
            month = HEBREW_MONTHS[part]
    
    if year and month and day:
        return {'year': year, 'month': month, 'day': day}
    
    return None

def parseGregorianDate(date_str):
    """Parse Gregorian date string into components."""
    # Try ISO format (YYYY-MM-DD)
    iso_match = re.match(r'(\d{4})-(\d{1,2})-(\d{1,2})', date_str)
    if iso_match:
        year, month, day = map(int, iso_match.groups())
        return {'year': year, 'month': month, 'day': day}
    
    # Try MM/DD/YYYY or DD/MM/YYYY
    slash_match = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', date_str)
    if slash_match:
        m1, m2, year = map(int, slash_match.groups())
        # Assume MM/DD/YYYY if first number > 12
        if m1 > 12:
            day, month = m1, m2
        else:
            month, day = m1, m2
        return {'year': year, 'month': month, 'day': day}
    
    # Try natural language (December 8, 2023)
    months = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12,
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }
    
    for month_name, month_num in months.items():
        if month_name in date_str.lower():
            # Extract day and year
            numbers = re.findall(r'\d+', date_str)
            if len(numbers) >= 2:
                day, year = int(numbers[0]), int(numbers[-1])
                # If year is 2-digit, assume 20xx
                if year < 100:
                    year += 2000
                return {'year': year, 'month': month_num, 'day': day}
    
    return None

def convertHebrewToGregorian(hebrew_date):
    """Convert Hebrew date to Gregorian using Hebcal API."""
    try:
        params = {
            'cfg': 'json',
            'hy': hebrew_date['year'],
            'hm': hebrew_date['month'],
            'hd': hebrew_date['day'],
            'h2g': '1',
            'strict': '1'
        }
        
        url = 'https://www.hebcal.com/converter?' + urllib.parse.urlencode(params)
        
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            
        if 'gy' in data and 'gm' in data and 'gd' in data:
            return {
                'year': data['gy'],
                'month': data['gm'],
                'day': data['gd'],
                'formatted': f"{data['gy']}-{data['gm']:02d}-{data['gd']:02d}"
            }
    except Exception:
        pass
    
    return None

def convertGregorianToHebrew(gregorian_date):
    """Convert Gregorian date to Hebrew using Hebcal API."""
    try:
        params = {
            'cfg': 'json',
            'gy': gregorian_date['year'],
            'gm': gregorian_date['month'],
            'gd': gregorian_date['day'],
            'g2h': '1',
            'strict': '1'
        }
        
        url = 'https://www.hebcal.com/converter?' + urllib.parse.urlencode(params)
        
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            
        if 'hy' in data and 'hm' in data and 'hd' in data:
            return {
                'year': data['hy'],
                'month': data['hm'],
                'day': data['hd'],
                'formatted': f"{data['hd']} {data['hm']} {data['hy']}"
            }
    except Exception:
        pass
    
    return None

def createResultItem(input_date, output_date, hebrew_to_gregorian):
    """Create a result item for display."""
    if hebrew_to_gregorian:
        input_text = f"{input_date['day']} {input_date['month']} {input_date['year']}"
        output_text = output_date['formatted']
        conversion_type = "Hebrew → Gregorian"
    else:
        input_text = f"{input_date['year']}-{input_date['month']:02d}-{input_date['day']:02d}"
        output_text = output_date['formatted']
        conversion_type = "Gregorian → Hebrew"
    
    return StandardItem(
        id=md_name,
        icon_factory=lambda: makeImageIcon(iconPath),
        text=output_text,
        subtext=f"{conversion_type}: {input_text}",
        actions=[
            Action("copy", "Copy to clipboard", lambda ot=output_text: setClipboardText(ot)),
            Action("copy-input", "Copy input date", lambda it=input_text: setClipboardText(it))
        ]
    )
