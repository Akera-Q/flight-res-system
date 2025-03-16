import React from 'react';
import Navbar from "../components/Navbar";
import FlightSearchForm from '../components/FlightSearchForm';
import { Dropdown } from 'react-bootstrap';
import "../App.css";
import InteractionTracker from '../services/InteractionTracker';


const App = () => {
  return (
    <>
    <InteractionTracker />
      <Navbar />
      <div className="parent">
        <div className="div1 photo-container">
        <div className='photo-wrapper left'>
            <img src="src/the_old_hunter.jpg" alt="hunter" />
            <img src="src/the_old_hunter.jpg" alt="hunter" />
            <img src="src/the_old_hunter.jpg" alt="hunter" />
          </div>
          <div className='photo-wrapper right'>
            <img src="src/the_old_hunter.jpg" alt="hunter" />
            <img src="src/the_old_hunter.jpg" alt="hunter" />
            <img src="src/the_old_hunter.jpg" alt="hunter" />
            <img src="src/the_old_hunter.jpg" alt="hunter" />
            <img src="src/the_old_hunter.jpg" alt="hunter" />
          </div>
        </div>
        <div className="div2">
          <h2>Compare flight deals from 100s of sites.</h2>
        </div>
        <div className="div3">
          <div className="flightButtonContainer">
            <button className="flightButtons">
              <i className="fa-solid fa-plane"></i>
            </button>
            <p>Flights</p>
          </div>
          <div className="flightButtonContainer">
            <button className="flightButtons">
              <i className="fa-solid fa-couch"></i>
            </button>
            <p>Stays</p>
          </div>
          <div className="flightButtonContainer">
            <button className="flightButtons">
              <i className="bi bi-car-front-fill"></i>
            </button>
            <p>Car Rental</p>
          </div>
        </div>
        <div className="div4">
          <ul class="nav ms-auto mb-2 mb-lg-0">
            <li className="nav-item dropdown">
            <Dropdown className="nav ms-auto mb-2 mb-lg-0">
              <Dropdown.Toggle
                  className="nav-link dropdown-toggle navbar-menu d-none d-lg-block"
                  href="#"
                  role="button"
                  aria-expanded="false"
                >
                  Flight Type
                </Dropdown.Toggle>
                <Dropdown.Menu>
                  <Dropdown.Item href="#"><a class="dropdown-item" href="#">Return</a></Dropdown.Item>
                  <Dropdown.Item href="#"><a class="dropdown-item" href="#">One-Way</a></Dropdown.Item>
                  <Dropdown.Item href="#"><a class="dropdown-item" href="#">Multi-City</a></Dropdown.Item>
                </Dropdown.Menu>
            </Dropdown>
              {/* <a class="nav-link dropdown-toggle navbar-menu" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                Flight Type
              </a>
              <ul class="dropdown-menu">
                <li><a class="dropdown-item" href="#">Return</a></li>
                <li><a class="dropdown-item" href="#">One-Way</a></li>
                <li><a class="dropdown-item" href="#">Multi-City</a></li>
              </ul> */}
            </li>
            <li class="nav-item dropdown">
            <Dropdown className="nav ms-auto mb-2 mb-lg-0">
            <Dropdown.Toggle
              className="nav-link dropdown-toggle navbar-menu d-none d-lg-block"
              href="#"
              role="button"
              aria-expanded="false"
            >
              Bags
            </Dropdown.Toggle>
            <Dropdown.Menu>
              <Dropdown.Item href="#"><p class="dropdown-item-text"><i class="fa-solid fa-suitcase"></i> Cabin Bag</p></Dropdown.Item>
              <Dropdown.Item href="#"><p class="dropdown-item-text"><i class="bi bi-suitcase-fill"></i> Checked Bag</p></Dropdown.Item>
              <Dropdown.Item href="#"><p class="dropdown-item-text">Per passenger.</p></Dropdown.Item>
            </Dropdown.Menu>
          </Dropdown>
              {/* <a class="nav-link dropdown-toggle navbar-menu" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                Bags
              </a>
              <ul class="dropdown-menu">
                <li><p class="dropdown-item-text"><i class="fa-solid fa-suitcase"></i> Cabin Bag</p></li>
                <li><p class="dropdown-item-text"><i class="bi bi-suitcase-fill"></i> Checked Bag</p></li>
                <li><p class="dropdown-item-text">Per passenger.</p></li>
              </ul> */}
            </li>
          </ul>
        </div>
        <div className="div5 d-flex">
          <FlightSearchForm />
        </div>
      </div>
      <img 
        src={`http://127.0.0.1:5000/static/heatmap.png?t=${Date.now()}`} 
        alt="User Heatmap" 
        style={{ width: "500px", border: "2px solid black" }}
      />
    </>
  );
};

export default App;
