import { useState, useCallback } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import { Toaster, toast } from "sonner";
import { Search, TrendingUp, Globe, DollarSign, Star, ExternalLink, Download, AlertTriangle, Loader2, ShoppingCart, Package, Store } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from "recharts";
import html2canvas from "html2canvas";
import jsPDF from "jspdf";
import { motion, AnimatePresence } from "framer-motion";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Example queries
const EXAMPLE_QUERIES = [
  "iPhone 15 price in India",
  "Dell Laptop under 50000",
  "Nike shoes",
  "Samsung TV 55 inch",
  "Sony headphones",
  "MacBook Pro in USA"
];

// Chart colors
const CHART_COLORS = ["#2563eb", "#7c3aed", "#10b981", "#f59e0b", "#ef4444", "#06b6d4", "#8b5cf6", "#ec4899"];

// Star rating component
const StarRating = ({ rating }) => {
  const fullStars = Math.floor(rating);
  const hasHalfStar = rating % 1 >= 0.5;
  
  return (
    <div className="flex items-center gap-1">
      {[...Array(5)].map((_, i) => (
        <Star
          key={i}
          className={`w-4 h-4 ${i < fullStars ? "text-amber-400 fill-amber-400" : i === fullStars && hasHalfStar ? "text-amber-400 fill-amber-400/50" : "text-slate-200"}`}
        />
      ))}
      <span className="ml-1 text-sm text-slate-600">{rating.toFixed(1)}</span>
    </div>
  );
};

// Availability badge
const AvailabilityBadge = ({ status }) => {
  const styles = {
    "In Stock": "bg-emerald-50 text-emerald-700 border-emerald-200",
    "Limited Stock": "bg-amber-50 text-amber-700 border-amber-200",
    "Pre-Order": "bg-blue-50 text-blue-700 border-blue-200"
  };
  
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${styles[status] || styles["In Stock"]}`}>
      {status}
    </span>
  );
};

// Product Card Component
const ProductCard = ({ product, index }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05, duration: 0.3 }}
      className="product-card"
      data-testid={`product-card-${index}`}
    >
      <img
        src={product.image}
        alt={product.name}
        className="product-card-image"
        loading="lazy"
      />
      <div className="product-card-content">
        <h3 className="product-card-title">{product.name}</h3>
        <p className="product-card-price">
          {product.currency_symbol}{product.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </p>
        <div className="product-card-source">
          <Store className="w-3 h-3" />
          {product.source}
        </div>
        <div className="flex items-center justify-between mt-2">
          <StarRating rating={product.rating} />
          <AvailabilityBadge status={product.availability} />
        </div>
        <p className="product-card-description">{product.description}</p>
        <a
          href={product.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 mt-4 text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors"
          data-testid={`view-source-${index}`}
        >
          View on {product.source}
          <ExternalLink className="w-4 h-4" />
        </a>
      </div>
    </motion.div>
  );
};

// Price Summary Component
const PriceSummary = ({ results, currencySymbol }) => {
  if (!results.length) return null;
  
  const prices = results.map(r => r.price);
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  const avgPrice = prices.reduce((a, b) => a + b, 0) / prices.length;
  
  return (
    <div className="price-summary-grid" data-testid="price-summary">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.1 }}
        className="price-summary-card min"
      >
        <p className="price-summary-label text-emerald-700">Lowest Price</p>
        <p className="price-summary-value text-emerald-600">
          {currencySymbol}{minPrice.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </p>
      </motion.div>
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.2 }}
        className="price-summary-card max"
      >
        <p className="price-summary-label text-red-700">Highest Price</p>
        <p className="price-summary-value text-red-600">
          {currencySymbol}{maxPrice.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </p>
      </motion.div>
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.3 }}
        className="price-summary-card avg"
      >
        <p className="price-summary-label text-blue-700">Average Price</p>
        <p className="price-summary-value text-blue-600">
          {currencySymbol}{avgPrice.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </p>
      </motion.div>
    </div>
  );
};

// Price Comparison Chart
const PriceComparisonChart = ({ results }) => {
  // Group by source and calculate average price
  const sourceData = {};
  results.forEach(r => {
    if (!sourceData[r.source]) {
      sourceData[r.source] = { total: 0, count: 0 };
    }
    sourceData[r.source].total += r.price;
    sourceData[r.source].count += 1;
  });
  
  const chartData = Object.entries(sourceData)
    .map(([source, data]) => ({
      source: source.length > 12 ? source.substring(0, 12) + "..." : source,
      fullSource: source,
      avgPrice: Math.round(data.total / data.count)
    }))
    .sort((a, b) => a.avgPrice - b.avgPrice)
    .slice(0, 8);
  
  return (
    <div className="chart-container" data-testid="price-chart">
      <h3 className="chart-title">Price Comparison by Source</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData} margin={{ top: 10, right: 10, left: 10, bottom: 40 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis 
            dataKey="source" 
            tick={{ fontSize: 12, fill: "#64748b" }}
            angle={-45}
            textAnchor="end"
            height={60}
          />
          <YAxis 
            tick={{ fontSize: 12, fill: "#64748b" }}
            tickFormatter={(value) => `${value.toLocaleString()}`}
          />
          <Tooltip
            formatter={(value) => [value.toLocaleString(), "Avg Price"]}
            labelFormatter={(label, payload) => payload[0]?.payload?.fullSource || label}
            contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0" }}
          />
          <Bar dataKey="avgPrice" fill="url(#colorGradient)" radius={[4, 4, 0, 0]} />
          <defs>
            <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#2563eb" />
              <stop offset="100%" stopColor="#7c3aed" />
            </linearGradient>
          </defs>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

// Source Distribution Chart
const SourceDistributionChart = ({ results }) => {
  const sourceCount = {};
  results.forEach(r => {
    sourceCount[r.source] = (sourceCount[r.source] || 0) + 1;
  });
  
  const chartData = Object.entries(sourceCount)
    .map(([source, count]) => ({ name: source, value: count }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 8);
  
  return (
    <div className="chart-container" data-testid="source-distribution-chart">
      <h3 className="chart-title">Results by Source</h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={100}
            paddingAngle={2}
            dataKey="value"
            label={({ name, percent }) => `${name.substring(0, 10)}${name.length > 10 ? "..." : ""} (${(percent * 100).toFixed(0)}%)`}
            labelLine={false}
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
            ))}
          </Pie>
          <Tooltip formatter={(value) => [value, "Products"]} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

// Data Sources Section
const DataSourcesSection = ({ dataSources }) => {
  const getSourceIcon = (type) => {
    switch (type) {
      case "Global Supplier": return <Globe className="w-5 h-5 text-blue-600" />;
      case "Local Market": return <Store className="w-5 h-5 text-emerald-600" />;
      default: return <ShoppingCart className="w-5 h-5 text-violet-600" />;
    }
  };
  
  const getSourceBadgeColor = (type) => {
    switch (type) {
      case "Global Supplier": return "bg-blue-50 text-blue-700 border-blue-200";
      case "Local Market": return "bg-emerald-50 text-emerald-700 border-emerald-200";
      default: return "bg-violet-50 text-violet-700 border-violet-200";
    }
  };
  
  return (
    <div data-testid="data-sources">
      <h3 className="text-lg font-semibold text-slate-800 mb-4 font-['Manrope']">Data Sources</h3>
      <div className="data-sources-grid">
        {dataSources.map((source, index) => (
          <a
            key={index}
            href={source.url}
            target="_blank"
            rel="noopener noreferrer"
            className="data-source-card"
            data-testid={`data-source-${index}`}
          >
            {getSourceIcon(source.type)}
            <div className="flex-1 min-w-0">
              <p className="font-medium text-slate-800 truncate">{source.name}</p>
              <Badge variant="outline" className={`mt-1 ${getSourceBadgeColor(source.type)}`}>
                {source.type}
              </Badge>
            </div>
            <ExternalLink className="w-4 h-4 text-slate-400" />
          </a>
        ))}
      </div>
    </div>
  );
};

// Search Unavailable Component
const SearchUnavailable = ({ query, message }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="search-unavailable"
      data-testid="search-unavailable"
    >
      <AlertTriangle className="w-12 h-12 text-amber-500 mx-auto mb-4" />
      <h2>Search Unavailable</h2>
      <p className="mb-4">We couldn't find results for "<strong>{query}</strong>"</p>
      <div className="text-left mt-6">
        <p className="font-medium text-amber-800 mb-2">Suggestions:</p>
        <ul className="list-disc list-inside text-amber-700 space-y-1">
          <li>Try using different keywords</li>
          <li>Check the spelling of your search</li>
          <li>Search for a similar or related product</li>
          <li>Use more general terms</li>
        </ul>
      </div>
    </motion.div>
  );
};

// Markdown renderer (simple)
const MarkdownContent = ({ content }) => {
  // Simple markdown parsing
  const parseMarkdown = (text) => {
    return text
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/^# (.*$)/gim, '<h1>$1</h1>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/^- (.*$)/gim, '<li>$1</li>')
      .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
      .replace(/\n/g, '<br />');
  };
  
  return (
    <div
      className="markdown-content"
      dangerouslySetInnerHTML={{ __html: parseMarkdown(content) }}
    />
  );
};

// Main Search Page Component
const SearchPage = () => {
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [searchResults, setSearchResults] = useState(null);
  const [isExporting, setIsExporting] = useState(false);

  const handleSearch = useCallback(async (searchQuery) => {
    const q = searchQuery || query;
    if (!q.trim()) {
      toast.error("Please enter a search query");
      return;
    }

    setIsLoading(true);
    setSearchResults(null);

    try {
      const response = await axios.post(`${API}/search`, {
        query: q.trim(),
        max_results: 50
      });
      
      setSearchResults(response.data);
      
      if (response.data.success) {
        toast.success(`Found ${response.data.results_count} results`);
      } else {
        toast.warning("Search unavailable for this query");
      }
    } catch (error) {
      console.error("Search error:", error);
      toast.error(error.response?.data?.detail || "Search failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }, [query]);

  const handleExampleClick = (exampleQuery) => {
    setQuery(exampleQuery);
    handleSearch(exampleQuery);
  };

  const handleExportPDF = async () => {
    if (!searchResults || !searchResults.success) return;
    
    setIsExporting(true);
    toast.info("Generating PDF...");
    
    try {
      const element = document.getElementById("results-container");
      if (!element) return;
      
      const canvas = await html2canvas(element, {
        scale: 2,
        useCORS: true,
        logging: false
      });
      
      const imgData = canvas.toDataURL("image/png");
      const pdf = new jsPDF({
        orientation: canvas.width > canvas.height ? "landscape" : "portrait",
        unit: "px",
        format: [canvas.width, canvas.height]
      });
      
      pdf.addImage(imgData, "PNG", 0, 0, canvas.width, canvas.height);
      pdf.save(`${searchResults.query.replace(/\s+/g, "_")}_price_comparison.pdf`);
      
      toast.success("PDF exported successfully!");
    } catch (error) {
      console.error("PDF export error:", error);
      toast.error("Failed to export PDF");
    } finally {
      setIsExporting(false);
    }
  };

  const currencySymbol = searchResults?.results?.[0]?.currency_symbol || "₹";

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <AnimatePresence>
        {!searchResults && (
          <motion.section
            initial={{ opacity: 1 }}
            exit={{ opacity: 0, height: 0 }}
            className="hero-gradient py-20 md:py-32"
          >
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className="text-center"
              >
                <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-900 font-['Manrope'] tracking-tight">
                  Find Any Product,{" "}
                  <span className="gradient-text">Compare Prices Globally</span>
                </h1>
                <p className="mt-6 text-lg text-slate-600 max-w-2xl mx-auto">
                  AI-powered search across global suppliers, local markets, and online marketplaces.
                  Get instant price comparisons and market insights.
                </p>
              </motion.div>

              {/* Search Form */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2, duration: 0.6 }}
                className="mt-10"
              >
                <div className="search-input-wrapper">
                  <Search className="search-icon w-5 h-5" />
                  <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                    placeholder="Search for any product... (e.g., laptop, shoes, TV)"
                    disabled={isLoading}
                    data-testid="search-input"
                  />
                  <button
                    onClick={() => handleSearch()}
                    disabled={isLoading}
                    className="submit-btn"
                    data-testid="search-button"
                  >
                    {isLoading ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      <Search className="w-5 h-5" />
                    )}
                  </button>
                </div>

                {/* Example Queries */}
                <div className="example-queries" data-testid="example-queries">
                  {EXAMPLE_QUERIES.map((eq, index) => (
                    <button
                      key={index}
                      onClick={() => handleExampleClick(eq)}
                      className="example-pill"
                      disabled={isLoading}
                      data-testid={`example-query-${index}`}
                    >
                      {eq}
                    </button>
                  ))}
                </div>
              </motion.div>

              {/* Feature Cards */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4, duration: 0.6 }}
                className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16"
              >
                <div className="feature-card">
                  <div className="feature-icon blue">
                    <Globe className="w-6 h-6" />
                  </div>
                  <h3 className="feature-title">Universal Search</h3>
                  <p className="feature-description">
                    Search any product across global and local marketplaces worldwide
                  </p>
                </div>
                <div className="feature-card">
                  <div className="feature-icon purple">
                    <TrendingUp className="w-6 h-6" />
                  </div>
                  <h3 className="feature-title">AI-Powered Analysis</h3>
                  <p className="feature-description">
                    Smart insights and recommendations powered by advanced AI
                  </p>
                </div>
                <div className="feature-card">
                  <div className="feature-icon green">
                    <DollarSign className="w-6 h-6" />
                  </div>
                  <h3 className="feature-title">Best Prices</h3>
                  <p className="feature-description">
                    Compare prices from multiple sources to find the best deals
                  </p>
                </div>
              </motion.div>
            </div>
          </motion.section>
        )}
      </AnimatePresence>

      {/* Compact Search Bar when results are shown */}
      {searchResults && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="sticky top-0 z-50 bg-white/90 backdrop-blur-lg border-b border-slate-200 py-4"
        >
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center gap-4">
              <h1 className="text-xl font-bold text-slate-800 font-['Manrope'] hidden sm:block">
                Price<span className="gradient-text">Nexus</span>
              </h1>
              <div className="flex-1 max-w-xl">
                <div className="search-input-wrapper" style={{ maxWidth: "100%" }}>
                  <Search className="search-icon w-4 h-4" />
                  <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                    placeholder="Search products..."
                    disabled={isLoading}
                    style={{ height: "48px", fontSize: "1rem" }}
                    data-testid="search-input-compact"
                  />
                  <button
                    onClick={() => handleSearch()}
                    disabled={isLoading}
                    className="submit-btn"
                    style={{ width: "40px", height: "40px" }}
                    data-testid="search-button-compact"
                  >
                    {isLoading ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Search className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="flex flex-col items-center justify-center py-20" data-testid="loading-state">
          <div className="loading-spinner mb-4"></div>
          <p className="text-slate-600 animate-pulse-soft">Searching multiple sources...</p>
        </div>
      )}

      {/* Search Results */}
      {searchResults && !isLoading && (
        <div id="results-container" className="results-container">
          {searchResults.success ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.4 }}
            >
              {/* Results Header */}
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
                <div>
                  <h2 className="text-2xl font-bold text-slate-800 font-['Manrope']" data-testid="results-title">
                    Results for "{searchResults.query}"
                  </h2>
                  <p className="text-slate-600 mt-1">
                    Found <span className="font-semibold text-blue-600">{searchResults.results_count}</span> products
                    {" • "}AI Model: <span className="font-mono text-sm">{searchResults.ai_model}</span>
                  </p>
                </div>
                <Button
                  onClick={handleExportPDF}
                  disabled={isExporting}
                  className="btn-gradient text-white rounded-full px-6"
                  data-testid="export-pdf-button"
                >
                  {isExporting ? (
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <Download className="w-4 h-4 mr-2" />
                  )}
                  Export PDF
                </Button>
              </div>

              {/* Price Summary */}
              <div className="mb-8">
                <PriceSummary results={searchResults.results} currencySymbol={currencySymbol} />
              </div>

              {/* Tabs for different views */}
              <Tabs defaultValue="products" className="mb-8">
                <TabsList className="grid w-full grid-cols-4 max-w-md">
                  <TabsTrigger value="products" data-testid="tab-products">Products</TabsTrigger>
                  <TabsTrigger value="charts" data-testid="tab-charts">Charts</TabsTrigger>
                  <TabsTrigger value="insights" data-testid="tab-insights">Insights</TabsTrigger>
                  <TabsTrigger value="sources" data-testid="tab-sources">Sources</TabsTrigger>
                </TabsList>

                <TabsContent value="products" className="mt-6">
                  <div className="product-grid" data-testid="product-grid">
                    {searchResults.results.map((product, index) => (
                      <ProductCard key={index} product={product} index={index} />
                    ))}
                  </div>
                </TabsContent>

                <TabsContent value="charts" className="mt-6">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <PriceComparisonChart results={searchResults.results} />
                    <SourceDistributionChart results={searchResults.results} />
                  </div>
                </TabsContent>

                <TabsContent value="insights" className="mt-6">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 font-['Manrope']">
                        <TrendingUp className="w-5 h-5 text-blue-600" />
                        Market Insights
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <MarkdownContent content={searchResults.response} />
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="sources" className="mt-6">
                  <DataSourcesSection dataSources={searchResults.data_sources} />
                </TabsContent>
              </Tabs>
            </motion.div>
          ) : (
            <SearchUnavailable query={searchResults.query} message={searchResults.message} />
          )}
        </div>
      )}

      {/* Footer */}
      <footer className="mt-auto py-8 border-t border-slate-200 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-slate-600">
            <span className="font-semibold font-['Manrope']">Price<span className="gradient-text">Nexus</span></span>
            {" "}• AI-Powered Global Price Comparison
          </p>
          <p className="text-sm text-slate-500 mt-2">
            Search results are generated for demonstration purposes
          </p>
        </div>
      </footer>

      <Toaster position="top-right" richColors />
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<SearchPage />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
