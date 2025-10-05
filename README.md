# Nasa Hackathon 2025

Welcome to the **Nasa Hackathon 2025 project**! This application was created for the NASA hackathon in 2025 for the [Will It Rain On My Parade?](https://www.spaceappschallenge.org/2025/challenges/will-it-rain-on-my-parade/) challenge.



## Setup

In this project as we are using the nasa earthdata, you'll need to create a account in their [site](https://urs.earthdata.nasa.gov/), and create a file called `.netrc` in the root of the project. In this file you'll have to put your username and password in this way:

```
machine urs.earthdata.nasa.gov login {{username}} password {{password}}
```

Without it, many endpoints of the application will not work;


## Start the project

To start developing in the project, you can use the scripts inside the ./scripts folder. The `init-shell.sh` script is for initing the ptyhon shell and the `development.sh` script is for you to start the flask app.


## Access Enpoint

This app only have one endpoint to access the data, it being this one:

```bash
{{url}}/api/forecast
```

this endpoint needs the the lat, long and chosen_data query params, if you dont set them, it will return you a error.