
import "../assets/styles/settings.css";
import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";


/**
 * interface for the component paramaeters
 *
 * @interface Props
 */
interface Props {
  /**
 * React Node components that should render
 */
  children: React.ReactNode;
  /**
 * URL when the component should be renderered
 */
  path: string;
  /**
 * optional render option - if the user wants to disable the rendering
 */
  render?: boolean;
  /**
 * option to enable to more advanced rendering option (default is false)
 */
  enable?: boolean;
}

/**
 * Component that handles more advanced rendering configurations
 * 
 * @component
 */
function AdvancedRendering({ children, path, enable }: Props) {
  const location = useLocation();
  const [currentPath, setCurrentPath] = useState(location.pathname);
  const [renderComponent, setRenderComponent] = useState(location.pathname == path ? true : false);

  /**
   * @description Keeps the state even if the user navigates outside the current url
   *
   * @returns {JSX.Element}
   */
  useEffect(() => {
    if (!enable) {
      return;
    }

    const isDiscoveryPath = location.pathname == "/discovery";
    const wasDiscoveryPath = currentPath == "/discovery";


    // console.log("tx", isDiscoveryPath, wasDiscoveryPath, renderComponent);
    if (isDiscoveryPath && wasDiscoveryPath && renderComponent == false) {
      setCurrentPath(location.pathname);
      setRenderComponent(true);
      return;
    }

    if (isDiscoveryPath && !wasDiscoveryPath) {
      console.log("to discovery");
      setCurrentPath(location.pathname);
      setRenderComponent(true);
      return;
    }

    // location changed away from discovery
    if (!isDiscoveryPath && wasDiscoveryPath) {
      console.log("from discovery");
      setCurrentPath(location.pathname);
      setRenderComponent(false);
      return;
    }

    // location changed outside of discovery
    setCurrentPath(location.pathname);
  }, [location]);

  /**
  * returns the React node components that should be rendered
  *
  * @returns {JSX.Element}
  */
  return (
    <>
      {children}
    </>
  );
}

export default AdvancedRendering;