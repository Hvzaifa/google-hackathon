import re

file_path = 'lib/screens/results_screen.dart'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

replacements = {
    'Colors.white': 'theme.colorScheme.surface',
    'AppTheme.kPurple900': 'theme.colorScheme.onSurface',
    'AppTheme.kPurple700': 'theme.colorScheme.primary',
    'AppTheme.kPurple400': 'theme.colorScheme.primary',
    'AppTheme.kPurple300': 'theme.colorScheme.secondary',
    'AppTheme.kPurple200': 'theme.dividerColor',
    'AppTheme.kPurple100': 'theme.dividerColor.withOpacity(0.5)',
    'AppTheme.kPurple50': 'theme.colorScheme.surfaceContainerHighest',
    'Colors.grey.shade400': 'theme.disabledColor',
    'Colors.grey.shade500': 'theme.disabledColor',
    'Colors.grey.shade600': 'theme.colorScheme.onSurface.withOpacity(0.6)',
    'Colors.grey[600]': 'theme.colorScheme.onSurface.withOpacity(0.6)',
}

# The only tricky part is ensuring we get inal theme = Theme.of(context); inside build methods
# We'll handle the replacements first
for old, new in replacements.items():
    content = content.replace(old, new)

# We also need to fix .withOpacity instead of .withValues(alpha: ...) if we use .withOpacity above, or we just stick to withValues
content = content.replace('.withOpacity(0.5)', '.withValues(alpha: 0.5)')
content = content.replace('.withOpacity(0.6)', '.withValues(alpha: 0.6)')

# Add inal theme = Theme.of(context); to build methods
content = content.replace('Widget _buildBody(BuildContext context, OrchestrationState state, double hPad) {', 'Widget _buildBody(BuildContext context, OrchestrationState state, double hPad) {\n    final theme = Theme.of(context);')
content = content.replace('Widget _buildLoadingState() {', 'Widget _buildLoadingState(BuildContext context) {\n    final theme = Theme.of(context);')
content = content.replace('_buildLoadingState()', '_buildLoadingState(context)')
content = content.replace('Widget _buildErrorState(BuildContext context, String error) {', 'Widget _buildErrorState(BuildContext context, String error) {\n    final theme = Theme.of(context);')

# _buildStatusBadge
content = content.replace('Widget _buildStatusBadge(String status) {', 'Widget _buildStatusBadge(BuildContext context, String status) {\n    final theme = Theme.of(context);')
content = content.replace('_buildStatusBadge(data.status!)', '_buildStatusBadge(context, data.status!)')

# _buildDataSourceBadge
content = content.replace('Widget _buildDataSourceBadge(String dataSource, bool isLive) {', 'Widget _buildDataSourceBadge(BuildContext context, String dataSource, bool isLive) {\n    final theme = Theme.of(context);')
content = content.replace('_buildDataSourceBadge(dataSource, isGoogleMapsData)', '_buildDataSourceBadge(context, dataSource, isGoogleMapsData)')

# _buildFallbackCard
content = content.replace('Widget _buildFallbackCard(String message) {', 'Widget _buildFallbackCard(BuildContext context, String message) {\n    final theme = Theme.of(context);')
content = content.replace('_buildFallbackCard(data.fallbackResponse!', '_buildFallbackCard(context, data.fallbackResponse!')

# _buildMatchingReason
content = content.replace('Widget _buildMatchingReason(String reason) {', 'Widget _buildMatchingReason(BuildContext context, String reason) {\n    final theme = Theme.of(context);')
content = content.replace('_buildMatchingReason(data.matchingReason!)', '_buildMatchingReason(context, data.matchingReason!)')

# _buildConfirmBookingCard
content = content.replace('Widget _buildConfirmBookingCard(bool isBooking) {', 'Widget _buildConfirmBookingCard(BuildContext context, bool isBooking) {\n    final theme = Theme.of(context);')
content = content.replace('_buildConfirmBookingCard(state.isBooking)', '_buildConfirmBookingCard(context, state.isBooking)')

# _buildAgentTraceSummary
content = content.replace('Widget _buildAgentTraceSummary(List traces) {', 'Widget _buildAgentTraceSummary(BuildContext context, List traces) {\n    final theme = Theme.of(context);')
content = content.replace('_buildAgentTraceSummary(data.agentTrace!)', '_buildAgentTraceSummary(context, data.agentTrace!)')

# _buildFeedbackButton
content = content.replace('Widget _buildFeedbackButton() {', 'Widget _buildFeedbackButton(BuildContext context) {\n    final theme = Theme.of(context);')
content = content.replace('_buildFeedbackButton()', '_buildFeedbackButton(context)')

# _buildPipelineSteps
content = content.replace('Widget _buildPipelineSteps() {', 'Widget _buildPipelineSteps(BuildContext context) {\n    final theme = Theme.of(context);')
content = content.replace('_buildPipelineSteps()', '_buildPipelineSteps(context)')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
