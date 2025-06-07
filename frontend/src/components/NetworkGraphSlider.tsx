// NetworkGraphSlider.tsx
import { Slider } from '@ui5/webcomponents-react';

interface SliderProps {
  topEdgeCount: number | 'all';
  setTopEdgeCount: (value: number | 'all') => void;
}

// Create label mapping for the slider
const sliderMarks = [
  { value: 4, label: 'All' },
  { value: 3, label: 'Top 3' },
  { value: 2, label: 'Top 2' },
  { value: 1, label: 'Top 1' },
  
];

export function NetworkGraphSlider({ topEdgeCount, setTopEdgeCount }: SliderProps) {
  return (
    <div style={{ width: '12vw' }}>
      {/* Custom Label Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
        {[...sliderMarks].reverse().map(mark => (
          <span key={mark.value} style={{ textAlign: 'center', width: '25%' }}>
            {mark.label}
          </span>
        ))}
      </div>

      {/* Slider */}
      <Slider
        max={4}
        min={1}
        step={1}
        value={topEdgeCount === 'all' ? 4 : topEdgeCount}
        onChange={(event) => {
          const val = Number(event.target.value);
          setTopEdgeCount(val === 4 ? 'all' : val);
        }}
        showTickmarks
        showTooltip={false}
        style={{ width: '100%' }}
      />
    </div>
  );
}
