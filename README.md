# Sports API Data Collection System

A comprehensive Python-based system for collecting, logging, and analyzing sports data from TheSports API with automated scheduling and field analysis capabilities.

## 🚀 Features

- **Automated Data Collection**: Fetches data from 6 API endpoints every minute via cron
- **Centralized Logging**: Clean, timestamped logs with Eastern timezone formatting
- **Daily File Rotation**: Automatic daily rotation of data files at midnight
- **Field Analysis**: Complete analysis of all JSON fields being fetched
- **Error Handling**: Robust error handling with detailed logging
- **Cron Integration**: Fully automated execution with system cron

## 📊 API Endpoints

The system collects data from these TheSports API endpoints:

1. **Live Matches** (`live`) - Real-time match data (~10-20 records)
2. **Match Details** (`details`) - Detailed match information (~993 records)
3. **Odds History** (`odds`) - Betting odds data (currently 0 records)
4. **Teams** (`team`) - Team information (1000 records)
5. **Competitions** (`competition`) - Competition data (1000 records)
6. **Countries** (`country`) - Country information (212 records)

**Total Records per Run**: ~3,200+ records

## 📁 Project Structure

```
├── config.py                      # Universal configuration and timezone settings
├── json_fetch(step1).py           # Main data collection script
├── all_fetched_json_fields.py     # Field analysis script
├── show_fields.py                 # Simple field viewer (backup)
├── raw_json(step1).py             # Alternative data collection script
├── main_process_logger.log         # Process execution logs
├── all_fetched_json_fields.log     # Field analysis results
├── json_fetch_data_YYYY-MM-DD.json # Daily data files
├── cron.log                       # Cron execution logs
└── README.md                      # This file
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.x
- Required Python packages (install via pip):
  ```bash
  pip install requests hashlib json logging datetime pytz
  ```

### Configuration
1. Update API credentials in `config.py`:
   ```python
   API_USER = "your_username"
   API_SECRET = "your_secret_key"
   ```

2. Set up cron job for automated execution:
   ```bash
   # Edit crontab
   crontab -e
   
   # Add this line for every-minute execution:
   * * * * * cd /root && /usr/bin/python3 /root/json_fetch\(step1\).py
   ```

## 🔧 Usage

### Manual Execution
```bash
# Run main data collection
python3 "json_fetch(step1).py"

# Analyze JSON fields
python3 all_fetched_json_fields.py

# Quick field preview
python3 show_fields.py
```

### Automated Execution
The system runs automatically every minute via cron, collecting fresh data and logging all activities.

## 📈 Data Analysis

### Field Analysis Results
The system identifies **69 unique fields** across all endpoints:

#### By Endpoint:
- **LIVE**: 13 fields (match scores, stats, timeline)
- **DETAILS**: 29 fields (comprehensive match info)
- **ODDS**: 2 fields (basic structure, no data currently)
- **TEAM**: 26 fields (team details, market values, players)
- **COMPETITION**: 26 fields (tournament info, rounds, stages)
- **COUNTRY**: 7 fields (country data, logos)

#### Key Field Categories:
- **Match Data**: `away_scores`, `home_scores`, `match_time`, `status_id`
- **Team Info**: `team_id`, `coach_id`, `market_value`, `foundation_time`
- **Competition**: `competition_id`, `season_id`, `round_count`, `title_holder`
- **Geographic**: `country_id`, `venue_id`, `country_logo`
- **Live Data**: `stats`, `incidents`, `tlive` (timeline)
- **Coverage**: `coverage.lineup`, `coverage.mlive`

## 📋 Logging System

### Log Files:
1. **`main_process_logger.log`** - Process execution details
2. **`all_fetched_json_fields.log`** - Complete field analysis
3. **`json_fetch_data_YYYY-MM-DD.json`** - Daily data storage
4. **`cron.log`** - System cron execution logs

### Log Format:
```
MM/DD/YYYY HH:MM:SS AM/PM | LEVEL | Message
```
All timestamps in Eastern Time (ET) with automatic DST handling.

## 🕐 Scheduling

### Current Cron Configuration:
- **Frequency**: Every minute (`* * * * *`)
- **Execution Time**: ~20-25 seconds per run
- **Daily Rotation**: Files rotate at midnight ET
- **Success Rate**: 100% (6/6 endpoints successful)

### Performance Metrics:
- **Average Records/Run**: 3,220
- **Execution Time**: 20-25 seconds
- **API Calls**: 6 per minute
- **Data Volume**: ~2MB+ per day

## 🔍 Monitoring

### Health Checks:
- Monitor `main_process_logger.log` for execution status
- Check cron logs for scheduling issues
- Verify daily file creation and rotation
- Track record counts for data consistency

### Error Handling:
- Automatic retry logic for failed API calls
- Detailed error logging with timestamps
- Graceful handling of network issues
- Comprehensive exception tracking

## 🌐 API Integration

### Authentication:
- MD5 signature-based authentication
- Automatic signature generation
- Secure credential management

### Rate Limiting:
- 1-second delays between API calls
- Respectful API usage patterns
- Error handling for rate limits

## 📊 Data Storage

### File Format:
```json
{
  "date": "2025-05-26",
  "created_at": "2025-05-26T01:53:01.698181",
  "entries": [
    {
      "timestamp": "2025-05-26T01:53:01.697815",
      "type": "api_data",
      "endpoint": "live",
      "records_count": 13,
      "status": "success",
      "data": { ... }
    }
  ]
}
```

### Data Retention:
- Daily files with automatic rotation
- Compressed storage for historical data
- Configurable retention policies

## 🚀 Future Enhancements

- [ ] Database integration (PostgreSQL/MySQL)
- [ ] Real-time data streaming
- [ ] Web dashboard for monitoring
- [ ] Advanced analytics and reporting
- [ ] API rate optimization
- [ ] Data validation and quality checks
- [ ] Alerting system for failures
- [ ] Historical data analysis tools

## 📝 License

This project is for educational and research purposes. Please ensure compliance with TheSports API terms of service.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues or questions:
1. Check the logs for error details
2. Verify cron job configuration
3. Ensure API credentials are valid
4. Review network connectivity

---

**Last Updated**: May 26, 2025  
**Version**: 1.0.0  
**Status**: Production Ready ✅ 