# Albert Hebrew Calendar Plugin

An Albert launcher plugin for converting Hebrew dates to Gregorian dates and vice versa using the Hebcal.com API.

## Features

- Convert Hebrew dates to Gregorian dates
- Convert Gregorian dates to Hebrew dates
- Multiple input format support
- Fast API integration with Hebcal.com
- Copy results to clipboard

## Installation

1. Copy this directory to your Albert Python plugins directory:
   ```bash
   ~/.local/share/albert/python/plugins/
   ```

2. Enable the plugin in Albert settings

3. Set the trigger keyword (default: `heb `)

## Usage

Type `hebcal ` followed by a date in any of these formats:

### Hebrew to Gregorian
- `hebcal 5784 Kislev 25`
- `hebcal 25 Kislev 5784`
- `hebcal Kislev 25, 5784`

### Gregorian to Hebrew
- `hebcal 2023-12-08`
- `hebcal 12/8/2023`
- `hebcal December 8, 2023`
- `hebcal Dec 8 2023`

## Supported Hebrew Months

- Tishrei, Cheshvan, Kislev, Tevet, Shvat, Adar, Adar1, Adar2
- Nisan, Iyyar, Sivan, Tamuz, Av, Elul

## API

This plugin uses the [Hebcal.com Hebrew Date Converter REST API](https://www.hebcal.com/home/219/hebrew-date-converter-rest-api).

## Requirements

- Albert launcher
- Python 3
- Internet connection for API calls

## License

MIT License - see LICENSE file for details.

## Author

Guy Khmelnitsky

## Version

1.0.0
