import React, { useState } from 'react';
import './SlidingSwitch.css';

const SlidingSwitch = ({ onVersionChange }) => {
    const [checked, setChecked] = useState(false);

    const handleToggle = () => {
        setChecked(!checked);
        // Call the passed onVersionChange with new version
        onVersionChange(checked ? 'default' : 'detailed');
    };

    return (
        <div className="container">
            <label>
                <input
                    type="checkbox"
                    hidden
                    checked={checked}
                    onChange={handleToggle}
                    className="switch-input"
                />
                <span className="switch"></span>
                <i className="indicator"></i>
            </label>
            <label>{checked ? "Detailed Version" : "Default Version"}</label>
        </div>
    );
};

export default SlidingSwitch;