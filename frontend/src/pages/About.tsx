import { useEffect, useRef, useState } from 'react';
import { Icon } from '@ui5/webcomponents-react';

import "@ui5/webcomponents-icons/dist/information.js";
import "@ui5/webcomponents-icons/dist/customer-financial-fact-sheet.js";
import "@ui5/webcomponents-icons/dist/map-3.js";
import "@ui5/webcomponents-icons/dist/ai.js";
import "@ui5/webcomponents-icons/dist/bar-chart.js";
import "@ui5/webcomponents-icons/dist/group.js";
import "@ui5/webcomponents-icons/dist/decline.js";

import '../assets/styles/About.css';

/**
 * Represent the meta data about a team member
 *
 * @interface TeamMember
 */
interface TeamMember {
  /**
   * The name of each team member
   */
  name: string;
}

/**
 * Metadata for each team and it's members
 *
 * @interface Team
 */
interface Team {
  /**
   * Gives each team a unique ID
   */
  id: string;
  /**
   * title represent each teams name
   */
  title: string;
  /**
   * the content of the team description
   */
  description: string;
  /**
   * a list of each team member
   */
  members: TeamMember[];
}

// stage-content-wrapper and stage-text-block can be implemented in Abouttest.css for further styling
const stagesData = [
  {
    id: 'stage0',
    iconName: "information",
    menuTitle: "0. Introduction",
    fullTitle: "Introduction to PVT - Business Process Simulation",
    content: (
      <div className="stage-content-wrapper">
        <p className="stage-text-block">
          Welcome to the <strong>PVT - Business Process Simulation Application</strong>. <br />
          <br />
          This application allows the user to conduct data-driven business process simulations.
          <br />
          It uses <strong>Simod</strong> and <strong>AgentSimulator</strong> to
          discover scenarios from uploaded event logs.
          <br />
          It then allows the user to simulate these scenarios, either as-is or what-if by manually
          changing parameters.
          <br />
          The application also provides a high level analysis of the simulation results.
          <br />
          <br />
          This application is split into five stages, this user manual will guide you through the process
          by clicking on the different stages in the side menu.
        </p>
      </div>
    )
  },
  {
    id: 'stage1',
    iconName: "customer-financial-fact-sheet",
    menuTitle: "1. Event logs",
    fullTitle: "Event logs",
    content: (
      <div className="stage-content-wrapper">
        <p className="stage-text-block">
          Begin by uploading event logs in <strong>.CSV</strong> or <strong>.XES</strong> format
          via the <strong>Event Logs</strong> page (see the navigation menu).
          Event logs uploaded in <strong>.XES</strong> format will automatically be converted to <strong>.CSV</strong>.
          Ensure your logs include the following required columns for compatibility:
        </p>
        <ul>
          <li><strong>case id</strong></li>
          <li><strong>activity</strong></li>
          <li><strong>resource</strong></li>
          <li><strong>start_time</strong></li>
          <li><strong>end_time</strong></li>
        </ul>
        <p className="stage-text-block">
          If your column names differ, there exists functionality to rename them when uploading.
          Additional columns are acceptable as long as the core requirements are met.
          Uploaded logs can be renamed or deleted.
        </p>
      </div>
    )
  },
  {
    id: 'stage2',
    iconName: "map-3",
    menuTitle: "2. Discovery",
    fullTitle: "Discovery",
    content: (
      <div className="stage-content-wrapper">
        <div className="two-column-layout">
          <div>
            <p className="stage-text-block">
              After uploading an event log, you can head to the <strong>Discovery</strong> page to extract the data
              from the event log.
              To extract the data from the event log you can use two different approaches:
            </p>
            <ul>
              <li><strong>Simod:</strong> Returns a traditional process model.</li>
              <li>
                <strong>AgentSimulator:</strong> Returns a probabilistic model that revolves around agents,
                which is equivalent to resources.
              </li>
            </ul>
            <p className="stage-text-block">
              After discovery, you will get a preview of the model with the option to either configure
              parameters (what-if) or run simulation directly (as-is).
            </p>
          </div>
        </div>
      </div>
    )
  },
  {
    id: 'stage3',
    iconName: "ai",
    menuTitle: "3-4. Configure & Simulate Scenarios",
    fullTitle: "Configure & Simulate Scenarios",
    content: (
      <div className="stage-content-wrapper">
        <p className="stage-text-block">
          After discovery, you'll manage both parameter configuration and
          simulation execution on the <strong>Simulation</strong> page.
          The Simulation page lists all your saved scenarios (both 'as-is' and 'what-if').
          You can easily filter them by name or discovery approach.
        </p>
        <div>
          <h3 style={{ color: '#333' }}>Configuring 'What-If' Scenarios:</h3>
          <p className="stage-text-block">
            You can select a discovered scenario and manually adjust its parameters to create 'what-if'
            variations.
            Based on the discovery approach (<strong>Simod</strong> or <strong>AgentSimulator</strong>),
            you can modify
            resource availability, alter activity durations,
            and define other critical operational variables
            to explore different hypothetical outcomes.
          </p>
        </div>
        <div>
          <h3 style={{ color: '#333' }}>Running Simulations:</h3>
          <p className="stage-text-block">
            Once you've selected the desired scenario, you can initiate the simulation.
            The underlying simulation technology (<strong>Simod</strong> or <strong>AgentSimulator</strong>)
            will correspond
            to the method used for its discovery, ensuring consistency.
          </p>
        </div>
      </div>
    )
  },
  {
    id: 'stage4',
    iconName: "bar-chart",
    menuTitle: "5. Analysis",
    fullTitle: "Analysis",
    content: (
      <div className="stage-content-wrapper">
        <p className="stage-text-block">
          The <strong>Analysis</strong> page provides detailed insights into your simulation results
          through performance metrics and comparative analysis tools.
        </p>
        <p className="stage-text-block">
          You can analyze <strong>Simod</strong> scenarios, <strong>AgentSimulator</strong> scenarios,
          or compare both approaches side by side using <strong>Cross Analysis</strong> mode. The user
          can also choose whether to show undefined values or not.
          Simply select your simulated scenarios and click <strong>Analyze Scenario</strong> to
          generate performance reports.
        </p>
      </div>
    )
  }
];

const teamsData: Team[] = [
  {
    id: 'team1',
    title: 'Team 1 - Backend Web Management',
    description: 'Responsible for the backend of the web application, including the database and the API.',
    members: [
      { name: 'Nils Johansson' }, { name: 'Alexander Hedlund' },
      { name: 'David Hannes Anders Malmbeck' }, { name: 'William Dingstad' },
      { name: 'Hinok Zakir Saleh' }, { name: 'Hugo Sjödin' }, { name: 'Jakob Vingren' },
      { name: 'Linus Svedberg' }, { name: 'Noel Hedlund' },
    ],
  },
  {
    id: 'team2',
    title: 'Team 2 - Frontend Visualization & Web Development',
    description: 'Responsible for the frontend of the web application, ' +
      'including the visualization and the user interface.',
    members: [
      { name: 'Algot Eriksson Granér' }, { name: 'Emil Johansson' }, { name: 'Erik Simonsson' },
      { name: 'Joel Stenlund' }, { name: 'Jonatan Westling' }, { name: 'Napat Wattanaputtakorn' },
      { name: 'Nils Bergling' }, { name: 'Robin Westberg' }, { name: 'Viktor Vikström' },
    ],
  },
  {
    id: 'team3',
    title: 'Team 3 - AgentSimulator',
    description: 'Responsible for incorporating AgentSimulator into the application, ' +
      'which is one of the core simulation engines.',
    members: [
      { name: 'Alexander Teglund' }, { name: 'Filip Kanon' }, { name: 'Gustav Johansson' },
      { name: 'Isak Holm' }, { name: 'Jack Edh' }, { name: 'Kevin Karlsson' },
      { name: 'Konrad Arns' }, { name: 'Konstantin Alexeyev' }, { name: 'Tomas Sjöström' },
    ],
  },
  {
    id: 'team4',
    title: 'Team 4 - Simod',
    description: 'Responsible for incorporating Simod into the application, ' +
      'which is one of the core simulation engines.',
    members: [
      { name: 'Algot Heimerson' }, { name: 'David Norén' }, { name: 'Jonatan Wincent' },
      { name: 'Manfred Alalehto Jeansson' }, { name: 'Rona Taha' }, { name: 'Sophie Vainio' },
      { name: 'Tuva Falk' }, { name: 'Viktor Lindström' },
    ],
  },
];

/**
 * Renders the About page for the PVT Business Process Simulation Application.
 * This page includes a user manual detailing application stages and a section introducing the development teams.
 * It features an interactive carousel for the user manual and modal pop-ups for team member details.
 */
const BPMNAboutPage = () => {
  const [currentStageIndex, setCurrentStageIndex] = useState(0);
  const sectionsRef = useRef<Array<HTMLElement | null>>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null);

  useEffect(() => {
    const currentSections = sectionsRef.current.filter(el => el !== null) as HTMLElement[];
    if (currentSections.length === 0) { return; }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1 }
    );

    currentSections.forEach((section) => {
      observer.observe(section);
    });

    // Close modal on Escape key press
    const handleEsc = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        closeModal();
      }
    };
    window.addEventListener('keydown', handleEsc);

    return () => {
      currentSections.forEach((section) => {
        observer.unobserve(section);
      });
      window.removeEventListener('keydown', handleEsc);
    };
  }, []);

  const addToRefs = (el: HTMLElement | null, index: number) => {
    if (el) {
      sectionsRef.current[index] = el;
    }
  };

  const handleMenuItemClick = (index: number) => {
    setCurrentStageIndex(index);
  };

  const handleQuadrantClick = (team: Team) => {
    setSelectedTeam(team);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedTeam(null); // Clear selected team
  };

  /**
  *
  * Generates a interactive page which gives an overview over the project and the teams behind it.
  *
  * @returns {JSX.Element}
  */
  return (
    <div className="aboutComponent">
      {/* Generates the side menu with items that describe the different section of the website */}
      <section
        className="content-section fade-in-section inspired-carousel-container"
        ref={(el) => addToRefs(el, 0)}
      >
        <div className="inspired-carousel-inner-wrapper">
          <div className="stages-side-menu">
            <div className="side-menu-header">
              <h4>USER MANUAL</h4>
            </div>
            <ul>
              {stagesData.map((stage, index) => (
                <li
                  key={stage.id}
                  className={`menu-item ${index === currentStageIndex ? 'active' : ''}`}
                  onClick={() => handleMenuItemClick(index)}
                  role="button"
                  tabIndex={0}
                  aria-pressed={index === currentStageIndex}
                  aria-label={stage.fullTitle}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      handleMenuItemClick(index);
                    }
                  }}
                >
                  <span className="menu-item-title">{stage.menuTitle}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* XX */}
          <div className="stage-content-display-area">
            {stagesData.map((stage, index) => (
              <div
                key={stage.id}
                className={`content-slide ${index === currentStageIndex ? 'active' : ''}`}
                aria-hidden={index !== currentStageIndex}
              >
                <div className="slide-internal-header">
                  <span className="section-icon"><Icon name={stage.iconName} /></span>
                  <h2 className="centerText">{stage.fullTitle}</h2>
                </div>
                <div className="content-actual">{stage.content}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Meet the team Section */}
      <section
        className="content-section fade-in-section team-details-section"
        ref={(el) => addToRefs(el, 1)}
      >
        <div>
          <div className="section-header-container">
            <span className="section-icon"><Icon name="group" /></span>
            <h2 className="centerText">Meet the teams</h2>
          </div>
          <p className="team-intro-paragraph">
            This application is the result of a collaborative effort by 35 students from Umeå University
            in the PVT course of 2025.
            The project team consisted of students from the Bachelor Programme in Computer Science,
            Master of Science Programme in Computing Science and Engineering
            and the Master of Science Programme in Interaction Technology and Design.
            The project team was divided into four sub-teams, each responsible for a different aspect
            of the application.
          </p>

          <div className="team-quadrant-grid">
            {teamsData.map((team) => (
              <div
                key={team.id}
                className="team-quadrant-item"
                onClick={() => handleQuadrantClick(team)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    handleQuadrantClick(team);
                  }
                }}
              >
                <h3>{team.title}</h3>
                <p>{team.description}</p>
                {/* Member names are now rendered in the modal */}
              </div>
            ))}
          </div>

        </div>
      </section>

      {/* Present information about specific teams */}
      {isModalOpen && selectedTeam && (
        <div className="modal-overlay" onClick={closeModal}
          role="dialog" aria-modal="true" aria-labelledby="modal-title">
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close-button" onClick={closeModal} aria-label="Close team details">
              <Icon name="decline" />
            </button>
            <h3 id="modal-title" className="modal-team-title">{selectedTeam.title}</h3>
            <p className="modal-description">{selectedTeam.description}</p>
            <div className="modal-members-area">
              <h4 className="modal-members-heading">Team Members:</h4>
              <div className="team-member-container">
                {selectedTeam.members.map((member) => (
                  <span key={member.name} className="team-member-pill">{member.name}</span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BPMNAboutPage;