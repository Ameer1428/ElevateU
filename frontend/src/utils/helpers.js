/**
 * Helper utility functions
 */

/**
 * Get initials from a name
 * @param {string} name - Full name
 * @returns {string} - Initials (max 2 characters)
 */
export const getInitials = (name) => {
  if (!name) return '?';

  const parts = name.trim().split(' ');
  if (parts.length === 1) {
    return parts[0].charAt(0).toUpperCase();
  }

  return `${parts[0].charAt(0)}${parts[parts.length - 1].charAt(0)}`.toUpperCase();
};

/**
 * Format date for display
 * @param {string|Date} date - Date to format
 * @returns {string} - Formatted date
 */
export const formatDate = (date) => {
  const options = {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  };
  return new Date(date).toLocaleDateString(undefined, options);
};

/**
 * Format duration for display
 * @param {string} duration - Duration string
 * @returns {string} - Formatted duration
 */
export const formatDuration = (duration) => {
  if (!duration) return 'N/A';

  // Simple formatting - can be enhanced
  return duration;
};

/**
 * Calculate completion percentage
 * @param {number} completed - Number of completed items
 * @param {number} total - Total number of items
 * @returns {number} - Completion percentage
 */
export const calculateCompletion = (completed, total) => {
  if (total === 0) return 0;
  return Math.round((completed / total) * 100);
};