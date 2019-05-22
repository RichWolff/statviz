class PolyfitStats():
    '''Poly fit creates various statistic visualizations to ... FINISH THIS.
       Parameters:
            - feature: a 1 column numpy series we'd like to use as independent variable
            - target: a 1 column numpy series we'd like to use as dependent variable
            - feature_units:
    '''
    def __init__(self,feature,target,feature_units=1):
        self.feature = feature
        self.target = target
        self.fit_bs_reps = False
        self.fit_reg_line = False
        self.fit_conf_int = False
        self.feature_units = feature_units

        if self.feature.name == None:
            self.feature.name = 'Feature'

    def confidence_intervals(self,ints=[2.5,97.5]):
        self.conf_intervals = ints

        if self.fit_bs_reps == False:
            self.fit_bs_replicates()

        self.conf_intervals_values = np.percentile(self.bs_slopes,ints)

        self.fit_conf_int = True

        return self.conf_intervals_values

    def r2(self):
        if self.fit_reg_line == False:
            self.fit_regression()
        return r2_score(self.target,self.pred_y)

    def corr(self):
        return np.corrcoef(x=self.feature,y=self.target)[0][1]

    def mse(self):
        if self.fit_reg_line == False:
            self.fit_regression()
        return mean_squared_error(self.target,self.pred_y)

    def rmse(self):
        if self.fit_reg_line == False:
            self.fit_regression()
        return np.sqrt(mean_squared_error(self.target,self.pred_y))

    def tgt_mean(self):
        return np.mean(self.target)

    def metrics(self,return_type=None,ax=None):
        '''Returns Corrleation of feature and target, r2,mse,&rmse of fit regressions line
        between the two, and confidence intervals of boot strap samples regression lines

        Can be returned as data or as '''

        if self.fit_conf_int == False:
            self.confidence_intervals()

        data = [self.tgt_mean(),
                self.corr(),
                self.r2(),
                self.mse(),
                self.rmse(),
                self.bs_slopes.min(),
                np.median(self.bs_slopes),
                self.bs_slopes.max(),
                self.conf_intervals_values[0],
                self.conf_intervals_values[1],
                self.feature_units,]

        df = pd.DataFrame(data,columns=['Values'],index=['Target Mean','Correlation','R2','MSE','RMSE','Increase Min','Increase Median','Increase Max','CI_Low','CI_High','Feature Units'])

        if return_type == 'df':
            return df

        elif return_type == 'img':
            assert not ax==None, "Please pass an axes object to plot img data on"

            from pandas.tools.plotting import table

            ax.xaxis.set_visible(False)  # hide the x axis
            ax.yaxis.set_visible(False)  # hide the y axis
            ax.set_frame_on(False)  # no visible frame, uncomment if size is ok
            tabla = table(ax, df, loc='upper right', colWidths=[0.17]*len(df.columns))  # where df is your data frame

            return tabla  # where df is your data frame

        else:
            return data

    def fit_bs_replicates(self,deg=1,bs_samples=1000,seed=None):
        np.random.seed(seed)
        indices = np.arange(len(self.feature))
        self.bs_intercepts = np.empty(bs_samples)
        self.bs_slopes = np.empty(bs_samples)
        self.bs_regs = np.empty(bs_samples,dtype=np.object)

        for i,n in enumerate(range(bs_samples)):
            bs_indices = np.random.choice(indices,len(indices))
            bs_x = self.feature[bs_indices]
            bs_y = self.target[bs_indices]
            sample_slope, sample_intercept = np.polyfit(bs_x,bs_y,deg=deg)

            sample_line_x = np.linspace(self.feature.min(),self.feature.max(),2)
            sample_line_y = [i*sample_slope+sample_intercept for i in sample_line_x]

            self.bs_intercepts[i] = sample_intercept
            self.bs_slopes[i] = sample_slope
            self.bs_regs[i] = [sample_line_x,sample_line_y]

        self.bs_intercepts = self.bs_intercepts * self.feature_units
        self.bs_slopes = self.bs_slopes * self.feature_units
        self.bs_regs = self.bs_regs * self.feature_units
        self.fit_bs_reps = True
        return None


    def fit_regression(self,deg=1):
        ## Get regression of line
        self.slope,self.intercept = np.polyfit(self.feature,self.target,deg=deg)
        self.observed_reg_x = np.linspace(self.feature.min(),self.feature.max(),2)
        self.observed_reg_y = [i*self.slope+self.intercept for i in self.observed_reg_x]
        self.pred_y = [x*self.slope+self.intercept for x in self.feature]
        self.fit_reg_line = True

    def histogram(self,ax=None, bins=30):
        assert not ax==None, "Please pass an axes object to plot histogram on"

        if self.fit_bs_reps == False:
            self.fit_bs_replicates()

        if self.fit_conf_int == False:
            self.confidence_intervals()

        ax.hist(self.bs_slopes,bins=bins)
        low, high = self.conf_intervals_values

        ymin,ymax = ax.get_ylim()
        ax.vlines(low,ymin,ymax*.65,color='r')
        ax.vlines(high,ymin,ymax*.65,color='r')
        xlabel = 'Expected {} Return Per {} Unit Increase of {}'.format(self.target.name,self.feature_units,self.feature.name)
        ax.set_xlabel(xlabel,size=12)
        ax.set_title('Expected ' + str(self.target.name) +' Return Per '+str(self.feature_units)+' Unit Increase Of '+ str(self.feature.name),size=16)
        ax.set_ylabel('Occurrences',size=12)
        return ax;

    def time_series(self,ax=None,normalize=True):
        assert not ax==None, "Please pass an axes object to plot time series on"
        series1 = self.feature.copy()
        series2 = self.target.copy()

        if normalize==True:
            series1 = series1.transform(zscore)
            series2 = series2.transform(zscore)

        if np.dtype(series1.index) == '<M8[ns]':
            _ = ax.plot(series1);
            _ = ax.plot(series2);
        else:
            _ = series1.plot(ax=ax);
            _ = series2.plot(ax=ax);

        ax.legend()
        ax.set_xlabel('Month',size=12)
        ax.set_ylabel('Standardized Values',size=12)
        ax.set_title(str(self.feature.name) + ' vs ' + str(self.target.name) + ' Over Time',size=16)
        return ax;


    def scatter(self, ax=None, regression_line=False, bootstrap_regression_lines=False, c=None ,cmap=None):
        assert not ax==None, "Please pass an axes object to plot scatter on"
        if bootstrap_regression_lines == True:
            if self.fit_bs_reps == False:
                self.fit_bs_replicates()
            for i in range(len(self.bs_regs)):
                #print(self.bs_regs[i][0],self.bs_regs[i][1])
                ax.plot(self.bs_regs[i][0],self.bs_regs[i][1],color='#FFCCCC',alpha=.25)

        if regression_line == True:
            if self.fit_reg_line == False:
                self.fit_regression()
            for i in range(len(self.bs_regs)):
                ax.plot(self.observed_reg_x,self.observed_reg_y,color='#FF5555')

        ax.scatter(self.feature,self.target,c=c,cmap=cmap)
        ax.set_xlabel(str(self.feature.name),size=12)
        ax.set_ylabel(str(self.target.name),size=12)
        ax.set_title(str(self.feature.name) +' vs ' +str(self.target.name),size=16)
        return ax;

    def resids(self,return_type='series',ax=None):
        if self.fit_reg_line == False:
            self.fit_regression()

        X = np.linspace(self.feature.min(),self.feature.max(),len(self.feature))
        pred = (X*self.slope)+self.intercept - self.target

        resids = zscore(self.target-pred)

        if return_type == 'series':
            return resids
        elif return_type == 'img':
            assert not ax==None, "Please pass an axes object to plot img data on"

            if np.dtype(resids.index) == '<M8[ns]':
                _ = ax.plot(resids,linestyle='None',marker='.');
            else:
                _ = resids.plot(ax=ax,marker='.',linestyle='None')

            _ = ax.set_ylabel('Standardized Residuals');
            _ = ax.set_xlabel(resids.index.name);
            _ = ax.set_title('Residuals From {} Predictions'.format(self.target.name));
            xmin,xmax = ax.get_xlim()
            _ = ax.hlines(0,xmin=xmin,xmax=xmax,color='black',alpha=.25,linestyle='--')
            _ = ax.hlines(1,xmin=xmin,xmax=xmax,color='black',alpha=.5,linestyle='--')
            _ = ax.hlines(-1,xmin=xmin,xmax=xmax,color='black',alpha=.5,linestyle='--')
            _ = ax.hlines(2,xmin=xmin,xmax=xmax,color='red',alpha=.35,linestyle='--')
            _ = ax.hlines(-2,xmin=xmin,xmax=xmax,color='red',alpha=.35,linestyle='--')
            return ax  # where df is your data frame
