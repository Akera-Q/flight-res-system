import React, { useState, useEffect } from 'react';
import { Dropdown } from 'react-bootstrap';
import flatpickr from 'flatpickr';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'flatpickr/dist/flatpickr.min.css';
import axios from 'axios';

const FlightSearchForm = ({ onSearchResults }) => {
  const [searchParams, setSearchParams] = useState({
    departure_code: '',
    destination_code: '',
    date_range: '',
    travellers: 1,
    class_type: 'economy'
  });
  const [airports, setAirports] = useState([]);
  const [loading, setLoading] = useState(false);

  // Fetch airports on component mount
  useEffect(() => {
    const fetchAirports = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/airports/');
        setAirports(response.data);
      } catch (error) {
        console.error('Error fetching airports:', error);
      }
    };
    fetchAirports();

    // Initialize date picker
    const datePicker = flatpickr("#DatePicker", {
      mode: "range",
      dateFormat: "Y-m-d",
      locale: "en",
      onChange: (selectedDates) => {
        if (selectedDates.length === 2) {
          setSearchParams(prev => ({
            ...prev,
            date_range: `${selectedDates[0].toISOString().split('T')[0]} to ${selectedDates[1].toISOString().split('T')[0]}`
          }));
        }
      }
    });

    return () => {
      datePicker.destroy();
    };
  }, []);

  const handleSwap = () => {
    setSearchParams(prev => ({
      ...prev,
      departure_code: prev.destination_code,
      destination_code: prev.departure_code
    }));
  };

  const handleSelectAirport = (type, code) => {
    setSearchParams(prev => ({
      ...prev,
      [type === 'from' ? 'departure_code' : 'destination_code']: code
    }));
  };

  const handleSelectClass = (classType) => {
    setSearchParams(prev => ({
      ...prev,
      class_type: classType.toLowerCase()
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      // Call your backend API with search parameters
      const response = await axios.get('http://localhost:8000/flights/search', {
        params: {
          departure_code: searchParams.departure_code,
          destination_code: searchParams.destination_code,
          date_range: searchParams.date_range,
          class_type: searchParams.class_type
        }
      });
      
      // Pass results to parent component
      onSearchResults(response.data);
    } catch (error) {
      console.error('Search error:', error);
      alert('Error searching flights. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="d-flex flightSearchForm" role="search" onSubmit={handleSubmit}>
      {/* Departure Airport Dropdown */}
      <div className="dropdown">
        <Dropdown>
          <Dropdown.Toggle 
            className='form-control me-2 btn no-arrow glass-button from-to' 
            id="from-dropdown" 
            type='button'
          >
            {searchParams.departure_code || 'From?'}
          </Dropdown.Toggle>
          <Dropdown.Menu>
            {airports.map(airport => (
              <Dropdown.Item 
                key={airport.code}
                onClick={() => handleSelectAirport('from', airport.code)}
              >
                {airport.name} ({airport.code})
              </Dropdown.Item>
            ))}
          </Dropdown.Menu>
        </Dropdown>
      </div>

      {/* Swap Button */}
      <div className="switchFromTo">
        <button 
          type="button" 
          className='form-control glass-button btn'
          onClick={handleSwap}
        >
          <i className="bi bi-arrow-left-right"></i>
        </button>
      </div>

      {/* Destination Airport Dropdown */}
      <div className="dropdown">
        <Dropdown>
          <Dropdown.Toggle 
            className='form-control me-2 btn no-arrow glass-button from-to' 
            id="to-dropdown" 
            type='button'
          >
            {searchParams.destination_code || 'To?'}
          </Dropdown.Toggle>
          <Dropdown.Menu>
            {airports.map(airport => (
              <Dropdown.Item 
                key={airport.code}
                onClick={() => handleSelectAirport('to', airport.code)}
              >
                {airport.name} ({airport.code})
              </Dropdown.Item>
            ))}
          </Dropdown.Menu>
        </Dropdown>
      </div>

      {/* Date Picker */}
      <div className="departureAndReturn">
        <input 
          className="form-control me-2 glass-button btn" 
          type="text" 
          id="DatePicker" 
          placeholder="Departure - Return"
        />
      </div>

      {/* Travellers & Class Dropdown */}
      <div className="dropdown">
        <Dropdown>
          <Dropdown.Toggle 
            className='form-control me-2 btn no-arrow glass-button' 
            id="dropdown" 
            type='button'
          >
            {`${searchParams.travellers} ${searchParams.travellers === 1 ? 'Traveller' : 'Travellers'}, ${searchParams.class_type}`}
          </Dropdown.Toggle>
          <Dropdown.Menu>
            <Dropdown.ItemText>Travellers</Dropdown.ItemText>
            <Dropdown.Item onClick={() => setSearchParams(prev => ({...prev, travellers: 1}))}>1 Adult</Dropdown.Item>
            <Dropdown.Item onClick={() => setSearchParams(prev => ({...prev, travellers: 2}))}>2 Adults</Dropdown.Item>
            <Dropdown.Item onClick={() => setSearchParams(prev => ({...prev, travellers: 3}))}>3 Adults</Dropdown.Item>
            <Dropdown.Item onClick={() => setSearchParams(prev => ({...prev, travellers: 4}))}>4 Adults</Dropdown.Item>
            <Dropdown.Divider />
            <Dropdown.ItemText>Class</Dropdown.ItemText>
            <Dropdown.Item onClick={() => handleSelectClass('Economy')}>Economy</Dropdown.Item>
            <Dropdown.Item onClick={() => handleSelectClass('Premium Economy')}>Premium Economy</Dropdown.Item>
            <Dropdown.Item onClick={() => handleSelectClass('Business')}>Business</Dropdown.Item>
            <Dropdown.Item onClick={() => handleSelectClass('First')}>First Class</Dropdown.Item>
          </Dropdown.Menu>
        </Dropdown>
      </div>

      {/* Search Button */}
      <div className="searchFlight">
        <button 
          className="btn btn-primary" 
          type="submit" 
          style={{boxShadow: '0 4px 10px rgba(0, 0, 0, 0.5)'}}
          disabled={loading || !searchParams.departure_code || !searchParams.destination_code || !searchParams.date_range}
        >
          {loading ? (
            <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
          ) : (
            <i className="bi bi-search"></i>
          )}
        </button>
      </div>
    </form>
  );
};

export default FlightSearchForm;
