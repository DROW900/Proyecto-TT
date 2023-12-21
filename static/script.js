// Referencias a los apartados dinámicos
const faseLimpieza = document.querySelector('#faseLimpieza');
const phMedido = document.querySelector('#phMedido');
const reguladorDefinido = document.querySelector('#reguladorDefinido');
const turbidezMedida = document.querySelector('#turbidezMedida');
const floculanteDefinido = document.querySelector('#floculanteDefinido');

addEventListener("DOMContentLoaded", initialize)

function initialize(){
    let anchoPantalla = screen.width;

    setInterval( async () => {
        // Hacemos la consulta de la información con el endpoint del servidor
        const valor =  await fetch("http://localhost:4000/ping");
        const parsedData = await valor.json();
        console.log(parsedData);

        // Hacemos los cambios según el bunche de información obtenida
        faseLimpieza.textContent = parsedData.instruccion;


        reguladorDefinido.classList.remove('sp-pendiente');
        reguladorDefinido.classList.add('sp-aceptable');
        reguladorDefinido.textContent = parsedData.turbidezDeterminadaEnNTU;

    }, 6000)


    /* Genera el formato del apartado circular según las fases necesarias */
    const circles = document.querySelectorAll('.element')

    const n = 10;  // numero de circulos
    const r = anchoPantalla < 720 ? 155 : 210 // radio
    console.log(r);


    let angulo = 0;
    let originX = circles[0].offsetLeft
    let originY = circles[0].offsetTop

    angulo += 0.01
    circles.forEach((element,i) =>{
    element.style.left = `${originX + r*Math.cos(angulo + 2*Math.PI/n*i)}px`
    element.style.top = `${originY + r*Math.sin(angulo + 2*Math.PI/n*i)}px`})
}