import React, { useState } from "react";
import { makeStyles } from "@material-ui/core/styles";
import Button from "@material-ui/core/Button";
import { Typography } from "@material-ui/core";

const useStyles = makeStyles({
  root: {
    background: "linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%)",
    border: 0,
    borderRadius: 3,
    boxShadow: "0 3px 5px 2px rgba(255, 105, 135, .3)",
    color: "white",
    height: 48,
    padding: "0 30px"
  }
});

const Predict = props => {
  const [predictedName, setPredictedName] = useState(
    "<Please Click Below To Predict Voice>"
  );
  const classes = useStyles();

  const handleClick = event => {
    console.log(predictedName);
    fetch(`/predict`, {
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json"
      }
    })
      .then(response => response.json())
      .then(data => setPredictedName(data.msg));
  };

  return (
    <div>
      <Typography align="center" color="secondary" variant="h3">
        {predictedName}
      </Typography>
      <Button className={classes.root} onClick={handleClick}>
        Predict Voice
      </Button>
    </div>
  );
};

export default Predict;
