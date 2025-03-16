import React from 'react';
import { useEffect } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import { Dropdown } from 'react-bootstrap';
import 'flatpickr/dist/flatpickr.min.css';
import flatpickr from 'flatpickr';  

const FlightSearchForm = () => {
  useEffect(() => {
    flatpickr("#DatePicker", {
      mode: "range",
      dateFormat: "Y-m-d",
      locale: "en",
    });
  }, []);

  // function TextAreaSwap() {
  //   const [fromText, setFromText] = useState('');
  //   const [toText, setToText] = useState('');
  
  //   const swapText = () => {
  //     const temp = fromText;
  //     setFromText(toText);
  //     setToText(temp);
  //   };
  return (
    <form className="d-flex flightSearchForm" role="search">

      <div className="dropdown">
        <Dropdown>
          <Dropdown.Toggle className='form-control me-2 btn no-arrow custom-dropdown-button from-to' id="from-dropdown" type='button' aria-label='From'>
            From?
          </Dropdown.Toggle>

          <Dropdown.Menu>
            <Dropdown.Item href="#/from-1">Option 1</Dropdown.Item>
            <Dropdown.Item href="#/from-2">Option 2</Dropdown.Item>
            <Dropdown.Item href="#/from-3">Option 3</Dropdown.Item>
          </Dropdown.Menu>
        </Dropdown>
      </div>


      <div className="switchFromTo">
        <button className='form-control '>
          <i className="bi bi-arrow-left-right"></i>
        </button>
      </div>

      <div className="dropdown">
        <Dropdown>
          <Dropdown.Toggle className='form-control me-2 btn no-arrow custom-dropdown-button from-to' id="to-dropdown" type='button' aria-label='To'>
            To?
          </Dropdown.Toggle>

          <Dropdown.Menu>
            <Dropdown.Item href="#/to-1">Option 1</Dropdown.Item>
            <Dropdown.Item href="#/to-2">Option 2</Dropdown.Item>
            <Dropdown.Item href="#/to-3">Option 3</Dropdown.Item>
          </Dropdown.Menu>
        </Dropdown>
      </div>


      <div className="departureAndReturn">
        <input className="form-control me-2" type="text" id="DatePicker" name="dateRange" placeholder="Departure - Return"/>
      </div>

      <div className="dropdown">
      <Dropdown>
      <Dropdown.Toggle className='form-control me-2 btn no-arrow custom-dropdown-button' id="dropdown" type='button' aria-label='Search'>
        Travellers & Class
      </Dropdown.Toggle>

      <Dropdown.Menu>
        <Dropdown.Item href="#/action-1">Action</Dropdown.Item>
        <Dropdown.Item href="#/action-2">Another action</Dropdown.Item>
        <Dropdown.Item href="#/action-3">Something else</Dropdown.Item>
      </Dropdown.Menu>
    </Dropdown>
      </div>
      {/* <Dropdown className="dropdown">
        <Dropdown.Toggle
          className="btn travellersAndClass form-control me-2 dropdown-toggle"
          id="dropdown-basic"
          type="button"
          data-bs-toggle="dropdown"
          aria-expanded="false"
          aria-label="Search"
          style={{ color: '#595C5F', backgroundColor: 'white', border: '1px solid #DEE2E6' }}
        >
          Travellers & Class
        </Dropdown.Toggle>
        <Dropdown.menu className="dropdown-menu">
          <Dropdown.Item><a className="dropdown-item" href="#">adult</a></Dropdown.Item>
          <Dropdown.Item><a className="dropdown-item" href="#">teenager</a></Dropdown.Item>
          <Dropdown.Item><a className="dropdown-item" href="#">some #### child</a></Dropdown.Item>
        </Dropdown.menu>
      </Dropdown> */}
      <div className="searchFlight">
        <button className="btn btn-primary" type="submit">
          <i className="bi bi-search"></i>
        </button>
      </div>
    </form>
  );
};

export default FlightSearchForm;
