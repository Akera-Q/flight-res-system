import React, { useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import { Dropdown, Offcanvas, Button, Modal, Col, Row, Form, InputGroup } from 'react-bootstrap';
import * as formik from 'formik';
import * as yup from 'yup';
// import FlightSearchForm from './FlightSearchForm'; //I'm just testing to see it on the navbar, will be edited later (**worked just fine**)


const Navbar = () => {
  // for the offcanvas
  const [showOffcanvas, setShowOffcanvas] = useState(false);  // State for the Offcanvas visibility
  const handleOffcanvasClose = () => setShowOffcanvas(false);  // Handle closing the offcanvas
  const handleOffcanvasShow = () => setShowOffcanvas(true);    // Handle opening the offcanvas

  //for the sign-in modal
  const [show, setShow] = useState(false);
  const handleClose = () => setShow(false);
  const handleShow = () => setShow(true);

  //for the sign-in form
  const { Formik } = formik;
  const schema = yup.object().shape({
    firstName: yup.string().required(),
    lastName: yup.string().required(),
    username: yup.string().required(),
    city: yup.string().required(),
    state: yup.string().required(),
    zip: yup.string().required(),
    terms: yup.bool().required().oneOf([true], 'Terms must be accepted'),
  });

  return (
    <nav className="navbar sticky-top">
      <div className="container-fluid">
        <div className="d-flex align-items-center">
          <button
            className="navbar-toggler"
            type="button"
            onClick={handleOffcanvasShow} 
            aria-controls="offcanvasNavbar"
            aria-label="Toggle navigation"
          >
            <span className="navbar-toggler-icon"></span>
          </button>

          <a className="navbar-brand ms-2" href="#" style={{ color: '#007bff' }}>
            EGY-FLIGHT&trade;
          </a>

          {/* Dropdown menu */}
          <Dropdown className="nav ms-auto mb-2 mb-lg-0">
            <Dropdown.Toggle
              className="nav-link dropdown-toggle navbar-menu d-none d-lg-block"
              href="#"
              role="button"
              aria-expanded="false"
            >
              More
            </Dropdown.Toggle>
            <Dropdown.Menu>
              <Dropdown.Item href="#">Reserved Flights <i className="fa-solid fa-plane-departure"></i></Dropdown.Item>
              <Dropdown.Item href="#">Favorites <i className="bi bi-heart-fill"></i></Dropdown.Item>
              <Dropdown.Item><hr className="dropdown-divider" /></Dropdown.Item>
              <Dropdown.Item href="#">Trending <i className="bi bi-stars"></i></Dropdown.Item>
            </Dropdown.Menu>
          </Dropdown>
        </div>
        
        {/* Offcanvas */}
        <Offcanvas show={showOffcanvas} onHide={handleOffcanvasClose}>
          <Offcanvas.Header closeButton>
            <Offcanvas.Title>Egy-Flight&trade;</Offcanvas.Title>
          </Offcanvas.Header>
          <Offcanvas.Body>
            <p class="nav-item">
              <a class="nav-link active" aria-current="page" href="#">Explore Trips <i class="bi bi-luggage-fill"></i></a>
            </p>
            <p class="nav-item">
              <a class="nav-link active" href="#">Your Flights <i class="bi bi-airplane-fill"></i></a>
            </p>
          </Offcanvas.Body>
        </Offcanvas>
        {/* the search thing in the navbar, just for testing */}
        {/* <FlightSearchForm /> */}
        {/* sign-in modal */}
        <form class="d-flex" role="sign-in">
            <button class="btn btn-outline-danger me-2" type="button"><i class="bi bi-heart"></i></button>
            
            <button onClick={handleShow} class="btn btn-outline-primary" data-bs-target="#exampleModalToggle" data-bs-toggle="modal" type="button"><i class="bi bi-person-circle"></i> Sign In</button>
          </form>
        <Modal show={show} onHide={handleClose}>
        <Modal.Header closeButton>
          <Modal.Title>Modal heading</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {/* beginning of the sign-in form, remember that we need to edit the (sizes or layout) and edit the input types and numbers */}
        <Formik
          validationSchema={schema}
          onSubmit={console.log}
          initialValues={{
            firstName: '',
            lastName: '',
            username: '',
            city: '',
            state: '',
            zip: '',
            terms: false,
          }}>
          {({ handleSubmit, handleChange, values, touched, errors }) => (
            <Form noValidate onSubmit={handleSubmit}>
              <Row className="mb-3">
                <Form.Group as={Col} md="4" controlId="validationFormik01">
                  <Form.Label>First name</Form.Label>
                  <Form.Control
                    type="text"
                    name="firstName"
                    placeholder="First Name"
                    value={values.firstName}
                    onChange={handleChange}
                    isValid={touched.firstName && !errors.firstName}
                  />
                  <Form.Control.Feedback>Looks good!</Form.Control.Feedback>
                </Form.Group>
                <Form.Group as={Col} md="4" controlId="validationFormik02">
                  <Form.Label>Last name</Form.Label>
                  <Form.Control
                    type="text"
                    name="lastName"
                    placeholder="Last Name"
                    value={values.lastName}
                    onChange={handleChange}
                    isValid={touched.lastName && !errors.lastName}
                  />

                  <Form.Control.Feedback>Looks good!</Form.Control.Feedback>
                </Form.Group>
                <Form.Group as={Col} md="4" controlId="validationFormikUsername">
                  <Form.Label>Username</Form.Label>
                  <InputGroup hasValidation>
                    <InputGroup.Text id="inputGroupPrepend">@</InputGroup.Text>
                    <Form.Control
                      type="text"
                      placeholder="Username"
                      aria-describedby="inputGroupPrepend"
                      name="username"
                      value={values.username}
                      onChange={handleChange}
                      isInvalid={!!errors.username}
                    />
                    <Form.Control.Feedback type="invalid">
                      {errors.username}
                    </Form.Control.Feedback>
                  </InputGroup>
                </Form.Group>
              </Row>
              <Row className="mb-3">
                <Form.Group as={Col} md="6" controlId="validationFormik03">
                  <Form.Label>City</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="City"
                    name="city"
                    value={values.city}
                    onChange={handleChange}
                    isInvalid={!!errors.city}
                  />

                  <Form.Control.Feedback type="invalid">
                    {errors.city}
                  </Form.Control.Feedback>
                </Form.Group>
                <Form.Group as={Col} md="3" controlId="validationFormik04">
                  <Form.Label>State</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="State"
                    name="state"
                    value={values.state}
                    onChange={handleChange}
                    isInvalid={!!errors.state}
                  />
                  <Form.Control.Feedback type="invalid">
                    {errors.state}
                  </Form.Control.Feedback>
                </Form.Group>
                <Form.Group as={Col} md="3" controlId="validationFormik05">
                  <Form.Label>Zip</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="Zip"
                    name="zip"
                    value={values.zip}
                    onChange={handleChange}
                    isInvalid={!!errors.zip}
                  />

                  <Form.Control.Feedback type="invalid">
                    {errors.zip}
                  </Form.Control.Feedback>
                </Form.Group>
              </Row>
              <Form.Group className="mb-3">
                <Form.Check
                  required
                  name="terms"
                  label="Agree to terms and conditions"
                  onChange={handleChange}
                  isInvalid={!!errors.terms}
                  feedback={errors.terms}
                  feedbackType="invalid"
                  id="validationFormik0"
                />
              </Form.Group>
              <Button type="submit">Submit form</Button>
            </Form>
          )}
        </Formik>
          
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleClose}>
            Close
          </Button>
          <Button variant="primary" onClick={handleClose}>
            Save Changes
          </Button>
        </Modal.Footer>
      </Modal>
      </div>
    </nav>
  );
};

export default Navbar;
