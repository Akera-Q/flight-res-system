import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';

const Modal = () => {
  return (
    <>
      <div
        className="modal fade"
        id="exampleModalToggle"
        aria-hidden="true"
        aria-labelledby="exampleModalToggleLabel"
        tabIndex="-1"
      >
        <div className="modal-dialog modal-dialog-centered">
          <div className="modal-content">
            <div className="modal-header">
              <h1 className="modal-title fs-5" id="exampleModalToggleLabel">
                <a className="navbar-brand ms-2" href="#" style={{ color: '#007bff' }}>
                  EGY-FLIGHT&TRADE;
                </a>
              </h1>
              <button
                type="button"
                className="btn-close"
                data-bs-dismiss="modal"
                aria-label="Close"
              ></button>
            </div>
            <div className="modal-body">
              Show a second modal and hide this one with the button below.
            </div>
            <form className="row g-3" style={{ padding: '20px' }}>
              {/* Form Inputs */}
            </form>
            <div className="modal-footer">
              <button
                className="btn btn-primary"
                data-bs-target="#exampleModalToggle2"
                data-bs-toggle="modal"
              >
                Open second modal
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Modal 2 */}
    </>
  );
};

export default Modal;
