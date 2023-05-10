// Get all cars
const cars = document.querySelectorAll('.Car');
const selection_box = document.getElementById('Filter_by');
const product_holder = document.getElementById('product_holder');

selection_box.addEventListener('change', getFilter);

function getFilter(e)
{
    mainSort(e.target.value)
}

function mainSort(orderBy)
{
    let carDati = [];

    for (let i = 0; i < cars.length; i++)
    {
        let car_data = getDataVariables(cars[i]);
        carDati.push([cars[i], car_data]);
    }

    displayCars(bigSort(carDati, orderBy));
}

function bigSort(dataToSort, orderBy)
{

    switch(orderBy)
    {
        case "Alphabetical":
            return dataToSort.sort(function(a, b)
            {
                return a[1][0].toLowerCase().localeCompare(b[1][0].toLowerCase());
            });
     
        case "Environmental_impact":
            return dataToSort.sort(function(a, b) {return a[1][2] - b[1][2]});
        case "Price":
            return dataToSort.sort(function(a, b) {return a[1][1] - b[1][1]});
        default:
            break;
    }
}

function displayCars(orderedCars)
{
    product_holder.innerHTML = "";

    for (let i = 0; i < orderedCars.length; i++)
    {
        product_holder.appendChild(orderedCars[i][0]);
    }
}

function getDataVariables(car)
{
    let m = car.childNodes[1];
    let p = m.name;
    p = p.split(',');
    p[1] = parseInt(p[1]);
    p[2] = parseInt(p[2]);

    return p;
}








