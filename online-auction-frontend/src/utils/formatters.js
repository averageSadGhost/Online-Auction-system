export const formatCurrency = (amount) => {
  const num = parseFloat(amount);
  if (isNaN(num)) return '$0.00';
  return `$${num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
};

export const formatDateTime = (isoString) => {
  if (!isoString) return '';
  const date = new Date(isoString);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  let hours = date.getHours();
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const ampm = hours >= 12 ? 'PM' : 'AM';
  hours = hours % 12;
  hours = hours ? hours : 12;
  return `${year}/${month}/${day} ${hours}:${minutes} ${ampm}`;
};

export const getTimeRemaining = (startDateTime) => {
  const now = new Date();
  const start = new Date(startDateTime);
  const diff = start - now;

  if (diff <= 0) return 'Starting soon';

  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

  let parts = [];
  if (days > 0) parts.push(`${days} day${days !== 1 ? 's' : ''}`);
  if (hours > 0) parts.push(`${hours} hour${hours !== 1 ? 's' : ''}`);
  if (minutes > 0 && days === 0) parts.push(`${minutes} minute${minutes !== 1 ? 's' : ''}`);

  return `Starting in ${parts.join(' ')}`;
};

export const formatTimer = (seconds) => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
};

export const getStatusColor = (status) => {
  switch (status) {
    case 'scheduled':
      return '#3b82f6'; // blue - matches --secondary
    case 'started':
      return '#10b981'; // green - matches --primary
    case 'ended':
      return '#ef4444'; // red - matches --error
    default:
      return '#6b7280'; // gray - matches --gray-500
  }
};
