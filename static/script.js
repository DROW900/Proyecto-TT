// Referencias a los apartados dinámicos
const numeroFase = document.querySelector('#faseActual')
const numeroFaseInfo = document.querySelector('#faseActualInfo')
const faseLimpieza = document.querySelector('#faseLimpieza');
const phMedido = document.querySelector('#phMedido');
const phMedidoPre = document.querySelector('#phMedidoPre');
const phMedidoRes = document.querySelector('#phMedidoRes');
const reguladorDefinido = document.querySelector('#reguladorDefinido');
const turbidezMedida = document.querySelector('#turbidezMedida');
const turbidezMedidaRes = document.querySelector('#turbidezMedidaRes');
const floculanteDefinido = document.querySelector('#floculanteDefinido');
const circles = document.querySelectorAll('.element')
const listaClasesImagenes = ["polused-water","ph","pour","algorithm","mix","wait","filter"];
let textosAModificarHTML = {
    phMedido,
    phMedidoPre,
    phMedidoRes,
    reguladorDefinido,
    turbidezMedida,
    turbidezMedidaRes,
    floculanteDefinido
}
let faseAnterior = -1;

addEventListener("DOMContentLoaded", initialize)

function initialize(){
    let anchoPantalla = screen.width;

    setInterval( async () => {
        // Hacemos la consulta de la información con el endpoint del servidor
        const valor =  await fetch("http://localhost:4000/getInfo");
        const parsedData = await valor.json();

        let faseActual = parsedData.fase;
        faseAnterior = faseActual-1;

        if (faseActual == 0){ // Fase 1
            cambiarCirculoGrafico(faseActual,circles[faseActual-1],circles[6])
        }
        if(faseAnterior != faseActual && faseActual > 0){ // Resto
            limpiarData();
            cambiarCirculoGrafico(faseActual,circles[faseActual-1],circles[faseAnterior-1]);
        }
        faseAnterior = faseActual;
        // Hacemos los cambios según el bunche de información obtenida
        numeroFase.textContent = faseActual;
        numeroFaseInfo.textContent = faseActual;
        faseLimpieza.textContent = parsedData.instruccion;

        if(parsedData.phMedidoInicial != 'Por medir'){
            phMedido.textContent = parsedData.phMedidoInicial;
            recolorearTextopH(phMedido)

        }
        if(parsedData.phMedidoMedio != 'Por medir'){
            phMedidoPre.textContent = parsedData.phMedidoMedio
            recolorearTextopH(phMedidoPre)
        }
        if(parsedData.phMedidoFinal != 'Por medir'){
            phMedidoRes.textContent = parsedData.phMedidoFinal
            recolorearTextopH(phMedidoRes)
        }

        if(parsedData.cantidadBicarbonato != 'Por definir'){
            reguladorDefinido.textContent = parsedData.cantidadBicarbonato + " g"
            reguladorDefinido.classList.remove('sp-pendiente')
        }

        if(parsedData.turbidezDeterminadaEnNTUInicial != 'Por medir')
            turbidezMedida.textContent = parsedData.turbidezDeterminadaEnNTUInicial + " NTU"

        if(parsedData.turbidezDeterminadaEnNTUFinal != 'Por medir')
            turbidezMedidaRes.textContent = parsedData.turbidezDeterminadaEnNTUFinal + " NTU"

        if(parsedData.cantidadFloculante != 'Por definir')
            floculanteDefinido.textContent = parsedData.cantidadFloculante + " ml"
    }, 5000)


    /* Genera el formato del apartado circular según las fases necesarias */

    const n = 7;  // numero de circulos
    const r = anchoPantalla < 720 ? 160 : 210 // radio


    let angulo = 0;
    let originX = circles[0].offsetLeft
    let originY = circles[0].offsetTop

    angulo += -1.11
    circles.forEach((element,i) =>{
    element.style.left = `${originX + r*Math.cos(angulo + 2*Math.PI/n*i)}px`
    element.style.top = `${originY + r*Math.sin(angulo + 2*Math.PI/n*i)}px`})
}

function recolorearTextopH(elementoHTML){
    ph = elementoHTML.textContent
    elementoHTML.classList.remove('sp-pendiente');
    if(ph > '8.5'){
        elementoHTML.classList.add('ph-alcalino')
    }else if(ph < '6.5'){
        elementoHTML.classList.add('ph-acido')
    }else{
        elementoHTML.classList.add('ph-neutro')
    }
}

function cambiarCirculoGrafico(faseActual,circuloActual,circuloAnterior = undefined){
    if(faseActual == 0){
        if(circuloAnterior){
            circuloAnterior.classList.remove("elementFaseActual")
        }
        circles.forEach((element, index) =>{
            let imagenActual = element.classList[2];
            element.classList.remove(imagenActual);
            element.classList.add(listaClasesImagenes[index]);
        })
        return;
    }
    if(faseActual == 1){
        circuloActual.classList.add("elementFaseActual")
        return;
    }
    circuloAnterior.classList.remove("elementFaseActual")
    circuloActual.classList.add("elementFaseActual")
}

function limpiarData(){
    for(clave in textosAModificarHTML){
        if(clave == 'phMedido' || clave == 'phMedidoPre' || clave == 'phMedidoRes' || clave == 'turbidezMedida' || clave == 'turbidezMedidaRes'){
            textosAModificarHTML[clave].textContent = 'Por medir';
        }else if(clave == 'reguladorDefinido' || clave == 'floculanteDefinido'){
            textosAModificarHTML[clave].textContent = 'Por definir'
        }
        let ultimaClase = textosAModificarHTML[clave].classList[0];
        textosAModificarHTML[clave].classList.remove(ultimaClase)
        textosAModificarHTML[clave].classList.add('sp-pendiente')
    }
}