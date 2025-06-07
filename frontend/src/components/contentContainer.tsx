import "../assets/styles/contentContainer.css";

/**
 * Handles the content container
 * 
 * @component
 */

interface Props {
  containerHeader?: React.ReactNode;
  children?: React.ReactNode;
  height?: string | number; // Accepts '40%', '60vh', etc.
}

function ContentContainer({ containerHeader, children, height }: Props) {
  return (
    <div className="contentContainer" style={{ height }}>
      {containerHeader && <h1 className="container-headline">{containerHeader}</h1>}
      {children}
    </div>
  );
}

export default ContentContainer;