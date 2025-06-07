import { useState } from 'react';
import { Button } from '@ui5/webcomponents-react';

const ApiTestButton = () => {
  const [message, setMessage] = useState<string>('');
  const [error, setError] = useState<string>('');

  const handleClick = async () => {
    try {
      const response = await fetch('/api/get-test-message-from-controller');
      const data = await response.json();
      setMessage(data.message);
      setError('');
    } catch (err: any) {
      console.error('Error fetching the API:', err.message);
      setError('Failed to fetch message.');
    }
  };

  return (
    <div>
      <Button onClick={handleClick}>
        Get Message from API
      </Button>
      <div style={{ marginTop: '20px', fontSize: '18px' }}>
        {message && <p>{message}</p>}
        {error && <p style={{ color: 'red' }}>{error}</p>}
      </div>
    </div>
  );
};

export default ApiTestButton;
