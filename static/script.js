// Referencias a los apartados dinámicos
const numeroFase = document.querySelector('#faseActual');
const descripcion = document.querySelector('#detallesFase');
const numeroFaseInfo = document.querySelector('#faseActualInfo');
const faseLimpieza = document.querySelector('#faseLimpieza');
const phMedido = document.querySelector('#phMedido');
const phMedidoPre = document.querySelector('#phMedidoPre');
const phMedidoRes = document.querySelector('#phMedidoRes');
const reguladorDefinido = document.querySelector('#reguladorDefinido');
const turbidezMedida = document.querySelector('#turbidezMedida');
const turbidezMedidaRes = document.querySelector('#turbidezMedidaRes');
const floculanteDefinido = document.querySelector('#floculanteDefinido');
const circles = document.querySelectorAll('.element')
const gota = document.querySelector('#imagenGota')

const listaClasesImagenes = ["polused-water","ph","pour","algorithm","mix","wait","filter"];
const listaClasesGota = ["fill0","fill14","fill28","fill42","fill56","fill70","fill84","fill98"];

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
        const valor =  await fetch("http://192.168.0.18:4000/getInfo");
        const parsedData = await valor.json();

        let faseActual = parsedData.fase;
        faseAnterior = faseActual-1;

        if (faseActual == 0){ // Fase 1
            cambiarCirculoGrafico(faseActual,circles[faseActual-1],circles[6]);
            uncheckCirculos();
        }
        if(faseAnterior != faseActual && faseActual > 0){ // Resto
            limpiarData();
            checkUntilNow(faseActual);
            cambiarCirculoGrafico(faseActual,circles[faseActual-1],circles[faseAnterior-1]);
        }

        actualizarGota(faseActual);

        faseAnterior = faseActual;
        // Hacemos los cambios según el bunche de información obtenida
        numeroFase.textContent = faseActual;
        numeroFaseInfo.textContent = faseActual;
        faseLimpieza.textContent = parsedData.instruccion;
        descripcion.textContent = parsedData.descripcion;

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

        if(parsedData.turbidezDeterminadaEnNTUInicial != 'Por medir'){
            turbidezMedida.textContent = parsedData.turbidezDeterminadaEnNTUInicial + " NTU"
            turbidezMedida.classList.remove('sp-pendiente')
        }

        if(parsedData.turbidezDeterminadaEnNTUFinal != 'Por medir'){
            turbidezMedidaRes.textContent = parsedData.turbidezDeterminadaEnNTUFinal + " NTU"
            turbidezMedidaRes.classList.remove('sp-pendiente')
        }

        if(parsedData.cantidadFloculante != 'Por definir'){
            floculanteDefinido.textContent = parsedData.cantidadFloculante + " ml"
            floculanteDefinido.classList.remove('sp-pendiente')
        }
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
    if(ph > 8.5){
        elementoHTML.classList.add('ph-alcalino')
        elementoHTML.textContent += " (Alto)"
    }else if(ph < 6.5){
        elementoHTML.classList.add('ph-acido')
        elementoHTML.textContent += " (Bajo)"
    }else{
        elementoHTML.classList.add('ph-neutro')
        elementoHTML.textContent += " (Neutro)"
    }
}

function uncheckCirculos(){
    circles.forEach(circulo =>{
        circulo.classList.remove("check");
    })
}

function checkUntilNow(faseActual){
    if(faseActual <= 1){
        return false;
    }
    let indice = faseActual - 2;
    circles.forEach((circulo, index) =>{
        if(index > indice)
            return true;
        circulo.classList.remove("check");
        circulo.classList.add("check");
    })
}

function actualizarGota(faseActual){
    let imagenActual = gota.classList[1];
    gota.classList.remove(imagenActual);
    gota.classList.add(listaClasesGota[faseActual]);
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
    circuloAnterior.classList.add("check");
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
