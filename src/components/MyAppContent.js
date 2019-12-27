import React, { Component } from "react";
import Grid from "@material-ui/core/Grid";
import { Typography } from "@material-ui/core";
import UploadButton from "./UploadButton";
import Predict from "./Predict";

class MyAppContent extends Component {
  constructor() {
    super();
    this.state = { value: "", file: null };
    this.handleChange = this.handleChange.bind(this);
  }

  // When File is uploaded this event chanes the state and assigns files inside state
  // Then that value is used to upload file
  handleChange(event) {
    this.setState({ value: event.target.value, file: event.target.files[0] });
  }

  render() {
    return (
      <div>
        <Grid container spacing={10}>
          <Grid item xs={12}>
            <Typography align="center" color="primary" variant="h3">
              Is it My Voice?
            </Typography>
          </Grid>
          {/* Upload File Section */}
          <Grid item xs={12}>
            <Typography align="center" color="secondary" variant="h3">
              <input
                type="file"
                value={this.state.value}
                onChange={this.handleChange}
              />
              <UploadButton
                fileToUpload={this.state.value}
                file={this.state.file}
              />
            </Typography>
          </Grid>
          {/* Predict Voice Section */}
          <Grid item xs={12}>
            <Typography align="center" color="secondary" variant="h3">
              <Predict />
            </Typography>
          </Grid>
        </Grid>
      </div>
    );
  }
}

export default MyAppContent;
