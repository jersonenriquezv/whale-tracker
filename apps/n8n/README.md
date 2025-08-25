# N8N Workflows for Whale Tracker v0

This directory contains N8N workflows for automated alerting and data processing in Whale Tracker v0.

## 📋 Overview

N8N is used for workflow automation, particularly for sending Telegram alerts based on various triggers from the Whale Tracker system.

## 🔄 Workflow Types

### 1. Whale Transaction Alerts
- **Trigger**: Large ETH transfers detected
- **Action**: Send Telegram notification with transaction details
- **Conditions**: Amount threshold, whale score, time-based filters

### 2. Liquidity Zone Alerts
- **Trigger**: Liquidity zone breaches or significant changes
- **Action**: Send Telegram notification with zone details
- **Conditions**: Price levels, volume thresholds, time windows

### 3. SMC Pattern Alerts
- **Trigger**: Smart Money Concept pattern completions
- **Action**: Send Telegram notification with pattern analysis
- **Conditions**: Pattern type, confidence score, market context

### 4. System Health Alerts
- **Trigger**: System issues or performance degradation
- **Action**: Send Telegram notification to administrators
- **Conditions**: Error rates, response times, service status

## 🚀 Setup Instructions

### 1. Access N8N
- Open your browser and go to: http://localhost:5678
- Default credentials: admin/password (configured in .env)

### 2. Import Workflows
- Workflows will be created manually in the N8N interface
- Templates will be provided in this directory

### 3. Configure Telegram Bot
- Ensure your Telegram bot token is set in the environment variables
- Test the bot connection in N8N

### 4. Test Workflows
- Use the test functionality in N8N to verify workflows
- Check that alerts are received in Telegram

## 📁 Workflow Files

### whale-transaction-alert.json
- Alerts for large whale transactions
- Includes transaction details and analysis

### liquidity-zone-alert.json
- Alerts for liquidity zone events
- Includes price levels and volume data

### smc-pattern-alert.json
- Alerts for SMC pattern completions
- Includes pattern analysis and predictions

### system-health-alert.json
- Alerts for system health issues
- Includes performance metrics and error details

## 🔧 Configuration

### Environment Variables
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `TELEGRAM_CHAT_ID`: Your Telegram chat ID
- `BACKEND_URL`: Backend API URL for data retrieval

### Webhook Endpoints
- `/webhook/whale-alert`: Triggered by whale transaction events
- `/webhook/liquidity-alert`: Triggered by liquidity zone events
- `/webhook/smc-alert`: Triggered by SMC pattern events
- `/webhook/system-alert`: Triggered by system health events

## 📝 Workflow Development

### Creating New Workflows
1. Open N8N interface
2. Create new workflow
3. Add trigger node (webhook, schedule, etc.)
4. Add processing nodes (filters, transformations)
5. Add action nodes (Telegram, HTTP requests)
6. Test and save workflow

### Best Practices
- Use descriptive names for workflows and nodes
- Add error handling and retry logic
- Test workflows thoroughly before deployment
- Monitor workflow execution logs
- Keep workflows simple and focused

## 🔍 Monitoring

### Workflow Execution
- Monitor workflow execution in N8N interface
- Check execution history and logs
- Set up alerts for workflow failures

### Alert Delivery
- Verify Telegram message delivery
- Monitor alert frequency and timing
- Track user engagement with alerts

## 🛠️ Troubleshooting

### Common Issues
1. **Webhook not receiving data**: Check backend API configuration
2. **Telegram messages not sent**: Verify bot token and chat ID
3. **Workflow execution errors**: Check node configuration and data format
4. **Performance issues**: Optimize workflow complexity and frequency

### Debug Steps
1. Check N8N execution logs
2. Verify environment variables
3. Test individual nodes
4. Check network connectivity
5. Review workflow logic

## 📚 Resources

- [N8N Documentation](https://docs.n8n.io/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Webhook Integration Guide](https://docs.n8n.io/integrations/builtin/trigger-nodes/n8n-nodes-base.webhook/)

## 🔄 Future Enhancements

- **Advanced Filtering**: More sophisticated alert conditions
- **Multi-channel Alerts**: Email, Slack, Discord integration
- **Alert Aggregation**: Batch multiple alerts into single messages
- **User Preferences**: Customizable alert settings per user
- **Analytics**: Alert effectiveness tracking and optimization
