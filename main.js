// 加载网站配置
fetch("conf.json", { cache: "reload" })
  .then(response => response.json())
  .then(data => {
    const canvas = document.createElement('canvas');
    canvas.style.display = 'none';
    document.body.appendChild(canvas);
    const ctx = canvas.getContext('2d');

    const grid = document.getElementById("siteGrid");
    for (const [name, site] of Object.entries(data.sites)) {
      const col = document.createElement("div");
      col.className = "col-12 col-sm-6 col-md-4 col-lg-3 mb-4";

      const card = document.createElement("div");
      card.className = "card card-site h-100 text-center";
      card.setAttribute('style', site.css);
      card.onclick = () => { window.location.href = site.address; };

      const img = document.createElement("img");
      img.src = site.logo;
      img.className = "card-img-top mx-auto d-block";
      img.alt = name;
      img.crossOrigin = "Anonymous";
      img.width = 60;
      img.height = 60;
      img.onload = function () {
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        const data = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
        const pixels = [];

        for (let i = 0; i < data.length; i += 4) {
          let r = data[i], g = data[i + 1], b = data[i + 2], a = data[i + 3];
          if (a === 0) continue;
          pixels.push([r, g, b]);
        }

        const colorMap = quantize(pixels, 16);
        const palette = colorMap.palette();

        const counts = new Map();
        for (let [r, g, b] of pixels) {
          const [nr, ng, nb] = colorMap.map([r, g, b]);
          const key = `${nr},${ng},${nb}`;
          counts.set(key, (counts.get(key) || 0) + 1);
        }

        const sortedColors = [...counts.entries()]
          .sort((a, b) => b[1] - a[1]);

        sortedColors.forEach(([color, count], i) => {
          const [r, g, b] = color.split(',').map(Number);
          const hex = "#" + [r, g, b].map(x => x.toString(16).padStart(2, "0")).join("");
          sortedColors[i][0] = hex;
        });

        console.log(name, ": Top 16 colors:", sortedColors);
      };

      const cardBody = document.createElement("div");
      cardBody.className = "card-body";

      const title = document.createElement("h5");
      title.className = "card-title";
      title.textContent = name;

      const desc = document.createElement("p");
      desc.className = "card-text text-secondary";
      desc.textContent = site.description;

      cardBody.appendChild(title);
      cardBody.appendChild(desc);
      card.appendChild(img);
      card.appendChild(cardBody);
      col.appendChild(card);
      grid.appendChild(col);
    }
    initScrollAnimation();
  })
  .catch(err => {
    console.error("加载 conf.json 失败:", err);
  });

// 滚动动画函数
function initScrollAnimation() {
  const cards = document.querySelectorAll('.card-site');
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  cards.forEach(card => observer.observe(card));
}
