import { useNavigate } from "react-router-dom";
import { Icon } from "@ui5/webcomponents-react";

import '@ui5/webcomponents-icons/dist/bar-chart.js';

import "../assets/styles/home.css";
import '@ui5/webcomponents-icons/dist/home.js';

/**
 * The first page the user is presented with after she has logged in.
 * 
 * @component
 */
function Home() {
  const navigate = useNavigate();

  /**
   * Generates a item list overview over the entire application
   * 
   * @param headline - main headline of the item
   * @param text - descriptive text of what it is.
   * @param button - text on the button
   * @param url - url sent to when clicking on the button
   * @param icon - icon before the headline
   * @returns {JSX.Element}
   */
  const generate = ({ headline = "", text = "", url = "", icon = "" }: iGenerate) => {
    return (
      <section className="item"
        onClick={() => {
          navigate(url);
        }}
      >
        <h2 className="itemHeadline">
          <Icon name={icon} className="itemIcon" />
          {headline}
        </h2>
        <p className="itemText">{text}</p>
      </section>
    );
  };

  /**
   * Generates a table overview over the webpage.
   * 
   * @returns {JSX.Element}
   */
  return (
    <div className="home">

      <h1 className="homeHeadline">Welcome to PVT - Business Process Simulation</h1>
      <div className="container">
        <div className="columns">
          <div className="column">

            {generate({
              headline: "Event Logs",
              text: "Upload view, and manage your event logs",
              url: '/eventlogs',
              icon: "customer-financial-fact-sheet"
            })}

            {generate({
              headline: "Simulation",
              text: "Run simulation on discovered scenarios and download results",
              url: '/simulation',
              icon: "ai"
            })}

            {generate({
              headline: "About",
              text: "Learn more about the project and the team behind it",
              url: '/about',
              icon: "hint"
            })}

          </div>
          <div className="column">
            {generate({
              headline: "Discovery",
              text: "Discover process models from your event logs and visualize them",
              url: '/discovery',
              icon: "map-3"
            })}

            {generate({
              headline: "Analysis",
              text: "Analys different simod and agent scenarios",
              url: '/analysis',
              icon: "bar-chart"
            })}
          </div>

        </div>
      </div>

      <div className="info">
        <Icon name="hint" className="infoIcon" />
        Tip: Use the navigation bar at the side to switch between pages at any time.
      </div>

    </div >
  );
}

/**
 * Represents metadata for the generated table list.
 *
 * @interface iGenerate
 */
interface iGenerate {
  /**
   * The main headline or title of the content item.
   */
  headline: string;
  /**
   * Describe text over the item
   */
  text: string;
  /**
   * URL the user is sent to when clicking on the element
   */
  url: string;
  /**
   * icon that is presented before the item headline. 
   */
  icon: string;
}

export default Home;
