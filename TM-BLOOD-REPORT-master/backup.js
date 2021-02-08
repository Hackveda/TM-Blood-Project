<style>
label {
  padding: 16px 48px;
  border: 3px solid #ffc872;
  border-radius: 48px;
  text-transform: uppercase;
  letter-spacing: 2px;
  font-weight: bold;
  color: #ffc872;
}

label:hover {
  transform: scale(1.04);
}

label.active {
  background-color: #ffc872;
  color: #242424;
}

label span {
  font-weight: normal;
}
</style>
{% render_field form.document type="file" name="" id='file'   %}
<label for='file' id="selector">
select file
</label>
<script>
var loader = function (e) {
  let file = e.target.files;
  let show = '<span>selected file : </span>' + file[0].name;
  let output = document.getElementById('selector');
  output.innerHTML = show;
  output.classList.add('active')
}
// event listener for input
let fileInput = document.getElementById("file");
fileInput.addEventListener('change', loader)
</script>
</div>
