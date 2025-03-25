
# Vinted Monitor Troubleshooting Guide

## Common Issues

### "No deals found - keeping watch"

**Cause:** This usually happens for one of these reasons:
1. Vinted is blocking the scraper's requests (most common)
2. Your profit threshold might be set too high
3. Your brand selection might be too narrow

**Solution:**
- The app will automatically use fallback demo data when Vinted blocks the scraper
- Try lowering your profit threshold in the sidebar
- Add more brands to your selection
- Increase your maximum price

### "Stuck on searching" / WebSocket errors

**Cause:** This is typically a connection issue between your browser and the Streamlit app.

**Solution:**
1. Try toggling the monitoring off and on again
2. Refresh the browser page
3. Wait a few minutes as the app will continue to retry connections automatically

### Slow performance

**Cause:** The scraper needs to be cautious to avoid being blocked by Vinted.

**Solution:**
- Increase your scan interval to 5+ minutes
- Reduce the number of brands you're monitoring at once
- The app is designed to run continuously, so let it work in the background

## How Anti-Scraping Works

Websites like Vinted have protection measures that can detect and block scrapers by:
1. Monitoring IP addresses making too many requests
2. Checking browser fingerprints
3. Using CAPTCHAs to block automated access

The app includes multiple features to work around these limitations:
- Rotating user agents
- Adding delays between requests
- Fallback to demo data
- Rate limiting and exponential backoff

## Best Practices

1. **Use longer scan intervals** (5+ minutes)
2. **Be patient** with the app - it's designed to find deals over time
3. **Set realistic profit thresholds** (around £10-15)
4. **Prioritize high-demand brands** like Nike, Jordan, and Supreme
