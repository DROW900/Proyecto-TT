addEventListener("DOMContentLoaded", initialize)

function initialize(){
    setInterval( async () => {
        const valor =  await fetch("http://localhost:4000/ping");
        console.log(await valor.json())
    }, 6000)

    const circles = document.querySelectorAll('.element')

    const n = 10;  // numero de circulos
    const r = 210 // radio

    let angulo = 0;
    let originX = circles[0].offsetLeft
    let originY = circles[0].offsetTop

    angulo += 0.01
    circles.forEach((element,i) =>{
    element.style.left = `${originX + r*Math.cos(angulo + 2*Math.PI/n*i)}px`
    element.style.top = `${originY + r*Math.sin(angulo + 2*Math.PI/n*i)}px`})
}