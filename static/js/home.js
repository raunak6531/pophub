// Dynamic Homepage JavaScript
$(document).ready(function() {
  
  // Theme configurations
  const themes = {
    movies: {
      title: "What's Hot in Movies 🎬",
      subtitle: "Discover trending blockbusters, hidden gems, and must-watch classics",
      gradient: "linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%)",
      bgColor: "rgba(255, 107, 107, 0.1)",
      accentColor: "#ff6b6b"
    },
    tv: {
      title: "Trending TV Shows 📺",
      subtitle: "Binge-worthy series and must-watch episodes",
      gradient: "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
      bgColor: "rgba(79, 172, 254, 0.1)",
      accentColor: "#4facfe"
    },
    music: {
      title: "What's Playing 🎵",
      subtitle: "Discover new beats, trending albums, and rising artists",
      gradient: "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
      bgColor: "rgba(78, 205, 196, 0.1)",
      accentColor: "#43e97b"
    },
    games: {
      title: "Gaming Universe 🎮",
      subtitle: "Epic adventures, trending games, and gaming culture",
      gradient: "linear-gradient(135deg, #fa709a 0%, #fee140 100%)",
      bgColor: "rgba(250, 112, 154, 0.1)",
      accentColor: "#fa709a"
    }
  };

  let currentTheme = 'movies';
  let contentCache = {};

  // Initialize
  loadTrendingContent('movies');
  
  // Category tab switching
  $('.category-tab').on('click', function() {
    const category = $(this).data('category');
    const theme = $(this).data('theme');
    
    if (category === currentTheme) return;
    
    // Update active tab
    $('.category-tab').removeClass('active');
    $(this).addClass('active');
    
    // Switch theme
    switchTheme(theme);
    
    // Switch content
    switchContent(category);
    
    currentTheme = category;
  });

  function switchTheme(theme) {
    const config = themes[theme];
    const container = $('#themeContainer');
    const body = $('body');

    // Update theme data attribute
    container.attr('data-current-theme', theme);
    body.attr('data-current-theme', theme);

    // Animate theme change
    container.addClass('theme-transitioning');

    setTimeout(() => {
      // Update text content
      $('#heroText').text(config.title);
      $('#heroSubtitle').text(config.subtitle);

      // Update CSS custom properties for theme (apply to entire page)
      document.documentElement.style.setProperty('--theme-gradient', config.gradient);
      document.documentElement.style.setProperty('--theme-bg', config.bgColor);
      document.documentElement.style.setProperty('--theme-accent', config.accentColor);
      document.documentElement.style.setProperty('--theme-primary', config.accentColor);
      document.documentElement.style.setProperty('--theme-secondary', config.bgColor);
      document.documentElement.style.setProperty('--theme-dark', config.bgColor.replace('0.1', '0.05'));

      // Update background animation
      updateBackgroundTheme(theme);

      // Update page background
      updatePageBackground(theme, config);

      container.removeClass('theme-transitioning');
    }, 150);
  }

  function updatePageBackground(theme, config) {
    // Update the entire page background with theme colors
    const body = $('body');
    const gradientBg = `linear-gradient(135deg, ${config.bgColor} 0%, var(--bg-primary) 50%, ${config.bgColor} 100%)`;

    body.css({
      'background': gradientBg,
      'transition': 'background 0.8s cubic-bezier(0.23, 1, 0.320, 1)'
    });

    // Update navbar theme
    $('.navbar').css({
      'background': `linear-gradient(135deg, ${config.bgColor.replace('0.1', '0.3')} 0%, rgba(255, 255, 255, 0.1) 100%)`,
      'border-bottom': `1px solid ${config.accentColor}`
    });
  }

  function updateBackgroundTheme(theme) {
    const shapes = $('.floating-shapes .shape');
    const colors = {
      movies: ['#ff6b6b', '#ee5a24', '#ff9ff3'],
      tv: ['#4facfe', '#00f2fe', '#667eea'],
      music: ['#43e97b', '#38f9d7', '#4ecdc4'],
      games: ['#fa709a', '#fee140', '#f093fb']
    };
    
    shapes.each(function(index) {
      const color = colors[theme][index % colors[theme].length];
      $(this).css('background', `linear-gradient(45deg, ${color}, ${color}88)`);
    });
  }

  function switchContent(category) {
    // Hide all sections
    $('.content-section').removeClass('active');
    
    // Show target section
    $(`#${category}Section`).addClass('active');
    
    // Load content if not cached
    if (!contentCache[category]) {
      loadTrendingContent(category);
    }
  }

  function loadTrendingContent(category) {
    if (contentCache[category]) return;
    
    contentCache[category] = true;
    
    switch(category) {
      case 'movies':
        loadMovieContent();
        break;
      case 'tv':
        loadTVContent();
        break;
      case 'music':
        loadMusicContent();
        break;
      case 'games':
        loadGamesContent();
        break;
    }
  }

  function loadMovieContent() {
    // Load trending movies
    loadCarouselContent('moviesTrending', '/api/trending/movies');
    loadCarouselContent('moviesTopRated', '/api/top-rated/movies');
    loadCarouselContent('moviesLatest', '/api/latest/movies');
  }

  function loadTVContent() {
    loadCarouselContent('tvTrending', '/api/trending/tv');
    loadCarouselContent('tvTopRated', '/api/top-rated/tv');
    loadCarouselContent('tvOnAir', '/api/on-air/tv');
  }

  function loadMusicContent() {
    loadCarouselContent('musicTrending', '/api/trending/music');
    loadCarouselContent('musicNew', '/api/new-releases/music');
    loadCarouselContent('musicFeatured', '/api/featured/music');
  }

  function loadGamesContent() {
    loadCarouselContent('gamesTrending', '/api/trending/games');
    loadCarouselContent('gamesTopRated', '/api/top-rated/games');
    loadCarouselContent('gamesNew', '/api/new-releases/games');
  }

  function loadCarouselContent(containerId, apiUrl) {
    const container = $(`#${containerId}`);

    // Show loading state
    container.html('<div class="loading-carousel"><div class="loading-spinner"></div><p>Loading trending content...</p></div>');

    // Use the proper trending API endpoints
    $.get(apiUrl)
      .done(function(data) {
        if (data.results && data.results.length > 0) {
          renderCarousel(container, data.results.slice(0, 10));
        } else {
          container.html('<div class="empty-state">No content available</div>');
        }
      })
      .fail(function(xhr, status, error) {
        console.error(`Failed to load ${apiUrl}:`, error);
        // Fallback to search API with popular terms
        const fallbackQueries = {
          moviesTrending: 'avengers',
          moviesTopRated: 'godfather',
          moviesLatest: 'spider',
          tvTrending: 'stranger',
          tvTopRated: 'breaking',
          tvOnAir: 'house',
          musicTrending: 'taylor swift',
          musicNew: 'drake',
          musicFeatured: 'billie eilish',
          gamesTrending: 'call of duty',
          gamesTopRated: 'zelda',
          gamesNew: 'fifa'
        };

        const query = fallbackQueries[containerId] || 'popular';
        const type = containerId.includes('movies') ? 'movie' :
                     containerId.includes('tv') ? 'tv' :
                     containerId.includes('music') ? 'album' : 'game';

        $.get('/api/search', { q: query, type: type })
          .done(function(data) {
            renderCarousel(container, data.results.slice(0, 10));
          })
          .fail(function() {
            container.html('<div class="error-state">Failed to load content</div>');
          });
      });
  }

  function renderCarousel(container, items) {
    if (!items.length) {
      container.html('<div class="empty-state">No content available</div>');
      return;
    }

    const carousel = $('<div class="carousel-track"></div>');
    
    items.forEach((item, index) => {
      const card = createTrendingCard(item, index);
      carousel.append(card);
    });

    container.html(carousel);
    
    // Add scroll controls
    addCarouselControls(container);
  }

  function createTrendingCard(item, index) {
    const typeColors = {
      movie: 'linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%)',
      tv: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
      album: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
      game: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
    };

    return $(`
      <div class="trending-card" style="animation-delay: ${index * 0.1}s" onclick="showDetail('${item.type}', '${item.id}')">
        <div class="trending-card-image">
          ${item.cover ? 
            `<img src="${item.cover}" alt="${item.title}" loading="lazy">` :
            `<div class="trending-placeholder">
              <i class="fas fa-image"></i>
            </div>`
          }
          <div class="trending-overlay">
            <button class="trending-play-btn">
              <i class="fas fa-play"></i>
            </button>
          </div>
        </div>
        <div class="trending-info">
          <div class="trending-badge" style="background: ${typeColors[item.type]}">
            ${item.type.toUpperCase()}
          </div>
          <h4 class="trending-title">${item.title}</h4>
          ${item.year ? `<p class="trending-year">${item.year}</p>` : ''}
        </div>
      </div>
    `);
  }

  function addCarouselControls(container) {
    const track = container.find('.carousel-track');
    const scrollAmount = 300;

    const controls = $(`
      <div class="carousel-controls">
        <button class="carousel-btn prev" disabled>
          <i class="fas fa-chevron-left"></i>
        </button>
        <button class="carousel-btn next">
          <i class="fas fa-chevron-right"></i>
        </button>
      </div>
    `);

    container.append(controls);

    controls.find('.prev').on('click', () => {
      track.animate({ scrollLeft: track.scrollLeft() - scrollAmount }, 300);
      updateControlStates();
    });

    controls.find('.next').on('click', () => {
      track.animate({ scrollLeft: track.scrollLeft() + scrollAmount }, 300);
      updateControlStates();
    });

    function updateControlStates() {
      const scrollLeft = track.scrollLeft();
      const maxScroll = track[0].scrollWidth - track.width();
      
      controls.find('.prev').prop('disabled', scrollLeft <= 0);
      controls.find('.next').prop('disabled', scrollLeft >= maxScroll);
    }

    track.on('scroll', updateControlStates);
  }

  // Show detail modal (import from browse.js or create simple version)
  window.showDetail = function(type, id) {
    // For now, redirect to browse page - later we can implement modal
    window.location.href = `/browse/#${type}-${id}`;
  };

});
